"""
This module provides functions to generate and format output documents for the GPT Batch Policy Processor.
It includes functions to create tables in Word documents, read data from Excel files, and format the output
documents with relevant information and metrics.
"""

from datetime import datetime
import os
import io
import pandas as pd
from src.validation import get_check_results_flag
from src.onedrive import get_graph_api_token, upload_file_to_onedrive
def get_output_fname(path_fxn, filetype="xlsx"):
    return path_fxn(f"results.{filetype}")

def output_metrics(doc, num_docs, t, num_pages, failed_pdfs):
    doc.add_heading(
        f"{num_docs} documents ({num_pages} total pages) processed in {t:.2f} seconds",
        4,
    )
    if len(failed_pdfs) > 0:
        doc.add_heading(f"Unable to process the following PDFs: {failed_pdfs}", 4)

def output_results_excel(relevant_articles, irrelevant_articles, output_path):
    """
    Writes the results into an Excel file with four worksheets:
      - 'Relevant Stage 1': Articles flagged as relevant by the headline but with insufficient extracted core details.
           (Contains only the article title and URL.)
      - 'Relevant Stage 2': Articles flagged as relevant by the headline that contain at least a project name and a company.
           (Includes extra columns such as Project name, Project scale, Year to be online, Technology to be used,
            Company, Potential Partners, Continent, Country, Project status, and a "Check Results" column.)
      - 'Irrelevant': Articles deemed irrelevant.
      - 'All Articles': A combined list of all articles (from irrelevant, Stage 1, and Stage 2) showing
           the article titles, URLs, and if they were discarded before stage 1 or stage 2.
    """
    tenant_id = os.getenv("OD_TENANT_ID")
    client_id = os.getenv("OD_CLIENT_ID")
    client_secret = os.getenv("OD_CLIENT_VALUE")
    drive_id = os.getenv("OD_DRIVE_ID")
    parent_item_id = os.getenv("OD_PARENT_ITEM")
    # Convert inputs to list of dictionaries if they are DataFrames.
    if isinstance(relevant_articles, pd.DataFrame):
        print("relevant is df")
        relevant_articles = relevant_articles.to_dict("records")
    if isinstance(irrelevant_articles, pd.DataFrame):
        print("irrelevant is df")
        irrelevant_articles = irrelevant_articles.to_dict("records")

    # Define simple columns for Stage 1 and Irrelevant sheets.
    simple_cols = ["title", "url"]

    # Define detailed columns for the Relevant Stage 2 sheet.
    detailed_cols = [
        "Internal ID", 
        "Justification",
        "Project name",
        "Project scale",
        "Year to be online",
        "Technology to be used",
        "Company",
        "Potential Partners",
        "Company type",
        "Project type",
        "Company has climate goals?",
        "Production plant",
        "Updated GEM Plant ID",
        "GEM wiki page link",
        "Latitude",
        "Longitude",
        "Coordinate accuracy",
        "Continent",
        "Country",
        "Iron production capacity (million tonnes per year)",
        "Steel production capacity (million tonnes per year)",
        "States iron & steel capacity?",
        "[ref] Iron or steel capacity",
        "Hydrogen generation capacity (MW)",
        "States CC & H2 capacity?",
        "[ref] CC or H2 capacity",
        "[ref] Investment",
        "Business proposed",
        "Project status",
        "Year construction began",
        "Actual start year",
        "[ref] Date of announcement",
        "Comments",
        "Lastest project news (yyyy-mm-dd)",
        "Lastly updated (yyyy-mm-dd)",
        "References 1",
        "Reference Article",
        "Check Results" 
    ]

    # First, filter out articles that have been flagged as irrelevant via the "irrelevant" key.
    newly_irrelevant = []
    filtered_relevant_articles = []
    for article in relevant_articles:
        if article.get("irrelevant"):  # If flagged as irrelevant by the secondary query.
            newly_irrelevant.append(article)
        else:
            filtered_relevant_articles.append(article)

    # Append newly flagged articles to the existing irrelevant_articles list.
    irrelevant_articles.extend(newly_irrelevant)
    print("Irrelevant:", irrelevant_articles)
    print("Relevant articles", filtered_relevant_articles)
    # Separate the remaining relevant articles into Stage 1 and Stage 2.
    stage1_articles = []  # Articles with insufficient details (did not reach Stage 2).
    stage2_articles = []  # Articles with sufficient details.
    for article in filtered_relevant_articles:
        if article.get("company", "").strip() and article.get("project_name", "").strip():
            stage2_articles.append(article)
        else:
            stage1_articles.append(article)

    print("Stage 1", stage1_articles)
    print("Stage 2", stage2_articles)
    df_stage1 = pd.DataFrame(stage1_articles, columns=simple_cols)

    # Helper function to build a detailed row for a Stage 2 article.
    def build_detailed_row(article):
        row_data = {col: "" for col in detailed_cols}
        # Core details.
        row_data["Project name"] = article.get("project_name", "")
        row_data["Project scale"] = article.get("scale", "")
        row_data["Year to be online"] = article.get("timeline", "")
        row_data["Technology to be used"] = article.get("technology", "")
        # Additional details.
        row_data["Company"] = article.get("company", "")
        row_data["Potential Partners"] = article.get("partners", "")
        row_data["Continent"] = article.get("continent", "")
        row_data["Country"] = article.get("country", "")
        row_data["Project status"] = article.get("project_status", "")
        row_data["Reference Article"] = article.get("title", "")
        row_data["References 1"] = article.get("url", "")
        
        # Use the full article text (if available) for fuzzy-checking.
        if article.get("full_text"):
            core_extracted = {
                "project_name": article.get("project_name", ""),
                "scale": article.get("scale", ""),
                "timeline": article.get("timeline", ""),
                "technology": article.get("technology", "")
            }
            flag, scores = get_check_results_flag(core_extracted, article["full_text"])
            row_data["Check Results"] = flag
        else:
            row_data["Check Results"] = ""
        return row_data

    detailed_rows = [build_detailed_row(article) for article in stage2_articles]
    df_stage2 = pd.DataFrame(detailed_rows, columns=detailed_cols)

    df_irrelevant = pd.DataFrame(irrelevant_articles, columns=simple_cols)


    # Build DataFrame for "All Articles"
    all_articles = []
    for article in stage1_articles:
        all_articles.append({
            "title": article.get("title", ""),
            "url": article.get("url", ""),
            "Discarded": "Discarded before Stage 2"
        })
    for article in stage2_articles:
        all_articles.append({
            "title": article.get("title", ""),
            "url": article.get("url", ""),
            "Discarded": ""
        })
    for article in irrelevant_articles:
        all_articles.append({
            "title": article.get("title", ""),
            "url": article.get("url", ""),
            "Discarded": "Discarded before Stage 1"
        })
    df_all = pd.DataFrame(all_articles, columns=["title", "url", "Discarded"])
    # Write the DataFrames to separate sheets in an Excel workbook.
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_stage1.to_excel(writer, sheet_name="Relevant Stage 1", index=False)
        df_stage2.to_excel(writer, sheet_name="Relevant Stage 2", index=False)
        df_irrelevant.to_excel(writer, sheet_name="Irrelevant", index=False)
        df_all.to_excel(writer, sheet_name="All Articles", index=False)
    buffer.seek(0)
    file_bytes = buffer.getvalue()
    output_fname = output_path
    graph_access_token = get_graph_api_token(tenant_id, client_id, client_secret)
    if not graph_access_token:
        print("Could not obtain Graph API token.")
        return
    upload_file_to_onedrive(file_bytes, drive_id, parent_item_id, output_fname, graph_access_token)
    buffer = io.BytesIO()
