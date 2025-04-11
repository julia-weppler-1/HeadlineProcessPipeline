import requests
import time
import urllib.parse
import logging
from src.read_json import parse_inoreader_feed
from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv
load_dotenv() 
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_inoreader_articles(folder_name, access_token):
    if not access_token:
        logger.error("No valid access token provided.")
        return []

    # Build the stream URL
    stream_id = urllib.parse.quote(f"user/-/label/{folder_name}", safe='')
    url = f"https://www.inoreader.com/reader/api/0/stream/contents/{stream_id}"

    params = {"n": 15}
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        logger.error("Failed to fetch articles: %s", response.text)
        return []
# def fetch_inoreader_articles(folder_name, access_token):
#     """
#     Fetch all articles from a given folder (label) that were published in the past week.
#     This function uses pagination (via the continuation token) and query parameters:
#       - n: max number of items per request (100)
#       - r: order ("o" for oldest first so that we can use the ot parameter)
#       - ot: start time (Unix timestamp) from which to return items
#     """
#     if not access_token:
#         logger.error("No valid access token provided.")
#         return []
    
#     # Compute the Unix timestamp for one week ago.
#     one_week_ago = int(time.time()) - 7 * 24 * 60 * 60
    
#     articles = []
#     n = 100
#     continuation = None
    
#     # Build the stream URL.
#     stream_id = urllib.parse.quote(f"user/-/label/{folder_name}", safe='')
#     base_url = f"https://www.inoreader.com/reader/api/0/stream/contents/{stream_id}"
#     headers = {"Authorization": f"Bearer {access_token}"}
    
#     # Loop until no continuation token is returned.
#     while True:
#         # Set parameters: using r="o" (oldest first) and ot with the start time.
#         params = {
#             "n": n,
#             "r": "o",
#             "ot": one_week_ago,
#             "output": "json"  # explicitly request JSON, though this endpoint returns JSON by default.
#         }
#         if continuation:
#             params["c"] = continuation
        
#         response = requests.get(base_url, headers=headers, params=params)
#         if response.status_code == 200:
#             json_data = response.json()
#             items = json_data.get("items", [])
#             if not items:
#                 logger.info("No more items returned; stopping pagination.")
#                 break
#             articles.extend(items)
            
#             continuation = json_data.get("continuation")
#             if not continuation:
#                 logger.info("No continuation token found; reached end of stream.")
#                 break
#         else:
#             logger.error("Failed to fetch articles: %s", response.text)
#             break
            
#     logger.info("Total items fetched: %d", len(articles))
#     return articles


def build_df_for_folder(folder_name, access_token):
    response = fetch_inoreader_articles(folder_name, access_token)
    df = parse_inoreader_feed(response)
    return df

def resolve_with_playwright(url):
    logging.info("Resolving URL via Playwright: %s", url)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        def block_resource(route, request):
            if request.resource_type in ["image", "stylesheet", "font"]:
                return route.abort()
            return route.continue_()
        page.route("**/*", block_resource)
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(1000)
        except Exception as e:
            logging.error("Error during page.goto: %s", e)
        final_url = page.url
        browser.close()
        return final_url

def fetch_full_article_text(row):
    logging.info("Fetching article text for row with URL: %s", row.get("url"))
    real_url = row.get("url", "")
    logging.info("Extracted final URL: %s", real_url)
    try:
        from newspaper import Article  # Move inside function if needed
        article = Article(real_url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        logging.error("Error fetching article from %s: %s", real_url, e)
        return ""
    
