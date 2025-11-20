import os
import time
import logging
import traceback
import pandas as pd
from dotenv import load_dotenv
import datetime
from src.inoreader import build_df_for_folder, fetch_full_article_text, resolve_with_playwright
from src.query_gpt import new_openai_session, query_gpt_for_relevance_iterative, query_gpt_for_project_details, fetch_variable_info, extract_numeric_facts_with_quotes
from src.results import output_results_excel, get_output_fname
from src.questions import STEEL_NO, IRON_NO, CEMENT_NO, CEMENT_TECH, STEEL_IRON_TECH
from src.ino_client_login import client_login
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def obtain_inoreader_token():
    """
    Returns a valid Inoreader access token using the legacy ClientLogin method.
    """
    # 1) Pull creds out of the environment
    username  = os.getenv("USERNAME")
    password  = os.getenv("PASSWORD")
    token_url = "https://www.inoreader.com/oauth2/token"

    # 2) Fail early if any are missing
    missing = [var for var,val in [
        ("USERNAME", username),
        ("PASSWORD", bool(password)),   # we don’t print the actual password
        ("TOKEN_URL", token_url)
    ] if not val]
    if missing:
        logger.error("Missing env var(s) for ClientLogin: %s", missing)
        return None

    # 3) Call client_login with those parameters
    try:
        token = client_login()
    except Exception:
        logger.exception("client_login() threw an unexpected error")
        return None

    if token:
        os.environ["INOREADER_ACCESS_TOKEN"] = token
        return token

    logger.error("ClientLogin returned no token")
    return None



def run_pipeline():
    logger.info("Pipeline started.")
    openai_key = os.getenv("OPENAI_APIKEY")

    # Step 1: Get a valid token.
    access_token = obtain_inoreader_token()
    if not access_token:
        raise RuntimeError("Could not obtain a valid Inoreader access token.")

    folder_questions = {
        "LeadIT-Cement": CEMENT_NO,
        "LeadIT-Iron": IRON_NO,
        "LeadIT-Steel": STEEL_NO,
    }

    # Create GPT client
    openai_client, gpt_model, _ = new_openai_session(openai_key)

    any_folder_failed = False

    for folder, target_questions in folder_questions.items():
        domain = folder.split("-")[-1].lower()
        logger.info("Processing folder: %s", folder)

        try:
            headlines = build_df_for_folder(folder, access_token)
            logger.info("Fetched %d headlines from folder %s.", len(headlines), folder)

            if headlines.empty:
                logger.error("No headlines fetched for folder: %s", folder)
                # Treat this as a failure for alerting, but continue to other folders
                any_folder_failed = True
                continue

            headlines["url"] = headlines["url"].apply(resolve_with_playwright)
            headlines["text_column"] = headlines["title"] + " " + headlines.get("summary", "")

            relevance_df = query_gpt_for_relevance_iterative(
                df=headlines,
                target_questions=target_questions,
                run_on_full_text=True,
                gpt_client=openai_client,
                gpt_model=gpt_model,
            )

            relevant_articles = []
            irrelevant_articles = []

            for _, row in relevance_df.iterrows():
                article_row = headlines.loc[row["index"]].copy()
                article_row["title"] = article_row["title"].split(" - ")[0].strip()
                url = article_row["url"]
                discard_reason = None

                try:
                    if row["relevant"] != "no":
                        # Fetch full text
                        try:
                            full_text = fetch_full_article_text({"url": url})
                            if full_text == "":
                                discard_reason = "Failed to fetch text"
                        except Exception as e:
                            discard_reason = "source blocks web scraping bots"
                            logger.error("Error fetching article from %s: %s", url, e)
                            full_text = ""

                        domain_local = folder.removeprefix("LeadIT-") if hasattr(str, "removeprefix") else (
                            folder[7:] if folder.startswith("LeadIT-") else folder
                        )

                        project_query = (
                            f"Based on the article below, is this about a project, plant, or demonstration in {domain_local}? "
                            f"Does it mention a project, plant, or demonstration in green {domain_local}? "
                            "This can include funding or contract/partnership updates and does it include some details about that project? "
                            "Answer ONLY as JSON with exactly one key “answer” whose value is “yes” or “no”.\n\n"
                            "Article text:\n\"\"\"\n" + full_text + "\n\"\"\""
                        )

                        try:
                            resp = fetch_variable_info(openai_client, gpt_model, project_query, run_on_full_text=True)
                            is_project = resp.get("answer", "").strip().lower() == "yes"
                        except Exception as e:
                            logger.exception("Project yes/no gate failed for %s: %s", url, e)
                            is_project = False
                            if discard_reason is None:
                                discard_reason = f"Project classification failed: {e}"

                        if is_project:
                            if folder == "LeadIT-Cement":
                                technologies = CEMENT_TECH
                            else:
                                technologies = STEEL_IRON_TECH

                            try:
                                details = query_gpt_for_project_details(
                                    openai_client,
                                    gpt_model,
                                    full_text,
                                    technologies,
                                    domain_local,
                                )
                            except Exception as e:
                                logger.exception("Project detail extraction failed for %s: %s", url, e)
                                details = {}
                                if discard_reason is None:
                                    discard_reason = f"Project detail extraction failed: {e}"

                        else:
                            details = {}
                            if discard_reason is None:
                                discard_reason = f"This article did not seem to be about a green {domain_local} project."

                        article_info = {
                            "title": article_row["title"],
                            "url": url,
                            "full_text": full_text,
                            "discard_reason": discard_reason,
                            **details,
                        }
                        relevant_articles.append(article_info)

                    else:
                        irrelevant_articles.append(
                            {
                                "title": article_row["title"],
                                "url": url,
                                "discard_reason": discard_reason,
                            }
                        )

                except Exception as article_exc:
                    # One article is bad; log & move on
                    logger.exception(
                        "Error processing article '%s' in folder %s: %s",
                        article_row.get("title", "Unknown Title"),
                        folder,
                        article_exc,
                    )
                    irrelevant_articles.append(
                        {
                            "title": article_row.get("title", "Unknown Title"),
                            "url": url,
                            "discard_reason": f"Pipeline error: {article_exc}",
                        }
                    )

            folder_df = pd.DataFrame(relevant_articles)
            output_fname = get_output_fname(folder, filetype="xlsx")
            output_results_excel(folder_df, irrelevant_articles, output_fname, domain=domain)

        except Exception as folder_exc:
            any_folder_failed = True
            logger.exception("Folder %s failed: %s", folder, folder_exc)

    if any_folder_failed:
        # This makes the overall pipeline fail in CI while still producing partial outputs.
        raise RuntimeError("One or more folders failed. See logs for details.")
    else:
        logger.info("Pipeline completed successfully.")

if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception:
        logger.exception("Pipeline failed.")
        raise