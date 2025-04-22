# ino_client_login.py
import os
import requests
import logging
from dotenv import load_dotenv

# Load environment variables from your .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def client_login(username: str, password: str, token_url: str) -> str | None:
    USERNAME = os.getenv("USERNAME")
    PASSWORD = os.getenv("PASSWORD")
    CLIENT_LOGIN_URL = "https://www.inoreader.com/accounts/ClientLogin"

    # --- NEW DEBUGGING GUARD ---
    if not USERNAME or not PASSWORD:
        logger.error(
            "ClientLogin env missing!  USERNAME=%r, PASSWORD set? %s",
            USERNAME, bool(PASSWORD)
        )
        return None
    # ----------------------------

    data = {"Email": username, "Passwd": password}
    response = requests.post(CLIENT_LOGIN_URL, data=data)

    if response.status_code == 200:
        for line in response.text.splitlines():
            if line.startswith("Auth="):
                token = line.split("=", 1)[1]
                logger.info("Successfully obtained auth token from ClientLogin.")
                return token
        logger.error("Auth token not found in ClientLogin response.")
        return None
    else:
        logger.error(
            "ClientLogin failed with status %s: %s",
            response.status_code, response.text
        )
        return None

if __name__ == "__main__":
    token = client_login()
    print("Retrieved Auth Token:", token)
