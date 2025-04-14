import os
import time
import logging
import traceback
import pandas as pd
from dotenv import load_dotenv
import datetime
# Import functions from your modules
from src.inoreader import build_df_for_folder, fetch_full_article_text, resolve_with_playwright
from src.query_gpt import new_openai_session, query_gpt_for_relevance_iterative, query_gpt_for_project_details
from src.results import output_results_excel
from src.questions import STEEL_NO, IRON_NO, CEMENT_NO, CEMENT_TECH, STEEL_IRON_TECH
from src.ino_client_login import client_login
from src.email_results import send_email_with_attachment
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def obtain_inoreader_token():
    """
    Returns a valid Inoreader access token using the legacy ClientLogin method.
    """
    token = client_login()  # Directly call client_login to get the Auth token.
    if token:
        os.environ["INOREADER_ACCESS_TOKEN"] = token
        return token
    else:
        logger.error("Failed to obtain a valid Inoreader auth token via ClientLogin.")
        return None


def run_pipeline():
    logger.info("Pipeline started.")
    try:
        # Step 1: Get a valid token (or perform OAuth flow if needed).
        openai_key = os.getenv("openai_apikey_leadit")
        access_token = obtain_inoreader_token()
        if not access_token:
            logger.error("Could not obtain a valid Inoreader access token. Exiting pipeline.")
            return

        # Define a mapping from folder names to their target questions.
        folder_questions = {
            "LeadIT-Cement": CEMENT_NO,
            "LeadIT-Iron": IRON_NO,
            "LeadIT-Steel": STEEL_NO,
        }

        # Create a GPT session.
        openai_client, gpt_model, _ = new_openai_session(openai_key)

        # Process each folder separately and save each result into its own Excel file.
        for folder, target_questions in folder_questions.items():
            logger.info("Processing folder: %s", folder)
            # Fetch headlines/articles for the folder.
            headlines = build_df_for_folder(folder, access_token)
            logger.info("Fetched %d headlines from folder %s.", len(headlines), folder)
            if headlines.empty:
                logger.error("No headlines fetched for folder: %s", folder)
                continue

            # Resolve URLs and add a text column.
            headlines["url"] = headlines["url"].apply(resolve_with_playwright)
            headlines["text_column"] = headlines["title"] + " " + headlines.get("summary", "")

            # Query GPT for relevance.
            relevance_df = query_gpt_for_relevance_iterative(
                df=headlines,
                target_questions=target_questions,
                run_on_full_text=True,
                gpt_client=openai_client,
                gpt_model=gpt_model
            )

            # Build two lists: one for relevant articles, one for irrelevant ones.
            relevant_articles = []
            irrelevant_articles = []
            print("relevance_df", relevance_df)
            for _, row in relevance_df.iterrows():
                article_row = headlines.loc[row["index"]]
                # Clean up the title.
                article_row["title"] = article_row["title"].split(" - ")[0].strip()
                url = article_row["url"]
                print("Row relevant?", article_row, row["relevant"])
                if row["relevant"] != "no":
                    full_text = fetch_full_article_text(article_row)
                    if folder == "LeadIT-Cement":
                        technologies = CEMENT_TECH
                    else:
                        technologies = STEEL_IRON_TECH
                    details = query_gpt_for_project_details(
                        openai_client,
                        gpt_model,
                        full_text,
                        technologies
                    )
                    article_info = {
                        "title": article_row["title"],
                        "url": url,
                        "full_text": full_text,
                        **details
                    }
                    relevant_articles.append(article_info)
                else:
                    # Collect the article as irrelevant.
                    irrelevant_articles.append({
                        "title": article_row["title"],
                        "url": url
                    })

            # Convert relevant articles to DataFrame.
            folder_df = pd.DataFrame(relevant_articles)
            print(folder_df)
            # Build an output filename for this folder.
            output_fname = os.path.join(os.getcwd(), f"results_{folder}.xlsx")
            # Save the DataFrame to an Excel file using both lists.
            output_results_excel(folder_df, irrelevant_articles, output_fname)
            subject = f"Inoreader Pipeline Results for {folder} - {datetime.now().strftime('%Y-%m-%d')}"
            body = f"Please find attached the results for {folder}."
            sender = os.getenv("SMTP_USERNAME")  # In our case, this is julia.weppler@sei.org
            receiver = "julia.weppler@sei.org"
            smtp_server = os.getenv("SMTP_SERVER")
            smtp_port = int(os.getenv("SMTP_PORT", "465"))
            smtp_username = os.getenv("SMTP_USERNAME")
            smtp_password = os.getenv("SMTP_PASSWORD")
            
            send_email_with_attachment(subject, body, output_fname,
                                       sender, receiver,
                                       smtp_server, smtp_port,
                                       smtp_username, smtp_password)
        logger.info("Pipeline completed successfully.")

    except Exception as e:
        logger.error("An error occurred: %s", traceback.format_exc())
        return

if __name__ == "__main__":
    run_pipeline()
