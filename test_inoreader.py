# test_inoreader.py
import logging
from src.ino_oauth import automate_oauth_flow
from src.ino_token import exchange_code_for_token
from src.inoreader import fetch_inoreader_articles, build_df_for_folder
from dotenv import load_dotenv
import os

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Step 1: Automate the OAuth login to get the authorization code
    auth_code = automate_oauth_flow()
    if not auth_code:
        logger.error("Failed to obtain authorization code.")
        return

    logger.info("Authorization code obtained: %s", auth_code)

    # Step 2: Exchange the authorization code for tokens
    token_data = exchange_code_for_token(auth_code)
    if not token_data:
        logger.error("Failed to exchange code for token.")
        return

    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    if not access_token:
        logger.error("No access token received.")
        return

    logger.info("Access Token: %s", access_token)
    # Optionally, save tokens to environment or a secure store
    # For testing, you might temporarily set them as environment variables:
    os.environ["INOREADER_ACCESS_TOKEN"] = access_token
    os.environ["INOREADER_REFRESH_TOKEN"] = refresh_token

    # Step 3: Use the access token to fetch articles
    folder_name = "LeadIT-Cement"  # Replace with your folder (label) name in Inoreader
    articles = build_df_for_folder(folder_name, access_token)
    logger.info("Fetched %d articles.", articles)

if __name__ == "__main__":
    main()
