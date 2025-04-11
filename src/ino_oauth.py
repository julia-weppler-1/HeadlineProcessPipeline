import os
import urllib.parse
import logging
import secrets
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Load environment variables from your .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read necessary credentials and values from environment
CLIENT_ID = os.getenv("inoreader_client_id")
CLIENT_SECRET = os.getenv("inoreader_key")
REDIRECT_URI = os.getenv("redirect_uri")
USERNAME = os.getenv("username")
PASSWORD = os.getenv("password")
SCOPE = "read"

# Generate a state parameter for the request
STATE = secrets.token_urlsafe(16)

# Build the authorization URL with the state parameter
AUTH_URL = (
    f"https://www.inoreader.com/oauth2/auth?"
    f"client_id={CLIENT_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    f"&response_type=code&scope={SCOPE}&state={STATE}"
)

def automate_oauth_flow():
    """Use a headless browser to log in, click 'Authorize' if needed, and retrieve the authorization code."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(AUTH_URL)

        try:
            # Wait for and fill the username field.
            page.wait_for_selector('input[name="username"]', timeout=15000)
            page.fill('input[name="username"]', USERNAME)

            # Fill the password field.
            page.wait_for_selector('input[name="password"]', timeout=15000)
            page.fill('input[name="password"]', PASSWORD)

            # Click the login button.
            page.click('button[type="submit"]')

            # Look for an 'Authorize' or 'Allow' button.
            try:
                # Attempt a selector that matches any button containing the text "Authorize" or "Allow".
                page.wait_for_selector('button:has-text("Authorize")', timeout=10000)
                page.click('button:has-text("Authorize")')
            except Exception as e:
                logger.info("No 'Authorize' button found with text 'Authorize': %s. Trying alternative.", e)
                try:
                    page.wait_for_selector('button:has-text("Allow")', timeout=5000)
                    page.click('button:has-text("Allow")')
                except Exception as e:
                    logger.info("No 'Allow' button found either; proceeding without clicking consent.")

            # Wait for redirection to complete.
            page.wait_for_url(f"{REDIRECT_URI}*", timeout=70000)
            final_url = page.url
        except Exception as e:
            logger.error("An error occurred during the OAuth flow: %s", e)
            browser.close()
            return None, None

        # Parse the final URL to extract the authorization code and state.
        parsed_url = urllib.parse.urlparse(final_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        auth_code = query_params.get("code", [None])[0]
        returned_state = query_params.get("state", [None])[0]

        browser.close()
        return auth_code, returned_state
