# ino_client_login.py
import os
import requests
import logging
from dotenv import load_dotenv

# Load environment variables from your .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def client_login():
    """
    Use the ClientLogin endpoint to get an Auth token.
    Returns:
        auth_token (str): The authentication token for API requests.
    """
    # Read credentials from the environment
    USERNAME = os.getenv("USERNAME")
    PASSWORD = os.getenv("PASSWORD")
    CLIENT_LOGIN_URL = "https://www.inoreader.com/accounts/ClientLogin"
    
    # Set up the required form data
    data = {
        "Email": USERNAME,
        "Passwd": PASSWORD,
    }
    
    # Send POST request to ClientLogin
    response = requests.post(CLIENT_LOGIN_URL, data=data)
    
    if response.status_code == 200:
        # The response contains a plain text block with lines like:
        # SID=null
        # LSID=null
        # Auth=G2UlCa...Fx
        auth_token = None
        for line in response.text.splitlines():
            if line.startswith("Auth="):
                auth_token = line[len("Auth="):]
                break
        if auth_token:
            logger.info("Successfully obtained auth token from ClientLogin.")
            return auth_token
        else:
            logger.error("Auth token not found in ClientLogin response.")
            return None
    else:
        # Handle various errors (503 if backend unreachable, 401 if credentials are invalid)
        logger.error("ClientLogin failed with status %s: %s", response.status_code, response.text)
        return None

if __name__ == "__main__":
    token = client_login()
    print("Retrieved Auth Token:", token)
