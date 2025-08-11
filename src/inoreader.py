import requests
import time
import urllib.parse
import logging
from src.read_json import parse_inoreader_feed
from playwright.sync_api import sync_playwright
import os
import datetime
from dotenv import load_dotenv
from requests.exceptions import HTTPError
from newspaper import Article
import requests
load_dotenv() 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
CLIENT_ID = os.getenv("INOREADER_CLIENT_ID")
APP_KEY = os.getenv("INOREADER_KEY")


def fetch_inoreader_articles(folder_name, access_token):
    """
    Fetch all articles from a given folder (label) that were published in the past week.
    This function uses pagination (via the continuation token) and query parameters:
      - n: max number of items per request (100)
      - r: order ("o" for oldest first so that we can use the ot parameter)
      - ot: start time (Unix timestamp) from which to return items
    """
    if not access_token:
        logger.error("No valid access token provided.")
        return []
    
    # Compute the Unix timestamp for one week ago.
    one_week_ago = int(time.time()) - 7 * 24 * 60 * 60
    
    articles = []
    n = 100
    continuation = None
    # Build the stream URL.
    stream_id = urllib.parse.quote(f"user/-/label/{folder_name}", safe='')
    base_url = f"https://www.inoreader.com/reader/api/0/stream/contents/{stream_id}"
    headers = {
        "Authorization": f"GoogleLogin auth={access_token}",
        "AppId": CLIENT_ID,  # Add the AppId header
        "appKey": APP_KEY
    }
    # Loop until no continuation token is returned.
    while True:
        # Set parameters: using r="o" (oldest first) and ot with the start time.
        params = {
                "n": n,
                "r": "n",  # newest first: 'ot' now acts as the end time (cutoff).
                "ot": one_week_ago,
                "output": "json"
            }
        if continuation:
            params["c"] = continuation
        
        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code == 200:
            json_data = response.json()
            items = json_data.get("items", [])
            if not items:
                logger.info("No more items returned; stopping pagination.")
                # break
            articles.extend(items)
            
            continuation = json_data.get("continuation")
            if not continuation:
                logger.info("No continuation token found; reached end of stream.")
                break
        else:
            logger.error("Failed to fetch articles: %s", response.text)
            break
            
    logger.info("Total items fetched: %d", len(articles))
    return articles


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
    real_url = row.get("url", "")
    logger = logging.getLogger(__name__)
    logger.info(f"Fetching article text for URL: {real_url}")

    # 1) Try a plain HTTP GET to check status
    try:
        resp = requests.get(real_url, timeout=15)
    except Exception as e:
        logger.error(f"Error fetching {real_url}: {e}")
        return ""

    # 2) If we got blocked, retry via Archive.org
    if resp.status_code == 403:
        archive_url = f"http://web.archive.org/web/{real_url}"
        logger.info(f"403 detected—retrying via Archive.org: {archive_url}")
        try:
            resp = requests.get(archive_url, timeout=15)
        except Exception as e:
            logger.error(f"Error fetching archive URL {archive_url}: {e}")
            return ""

    # 3) Make sure we now have a 200
    try:
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"Final fetch failed ({resp.status_code}): {e}")
        return ""

    # 4) Parse whatever HTML we got back
    html = resp.text
    article = Article(real_url)        # keeps metadata tied to original URL
    article.set_html(html)
    article.parse()

    text = (article.text or "").strip()
    if not text:
        logger.warning("No text extracted after parsing HTML from %s", resp.url)
    return text
