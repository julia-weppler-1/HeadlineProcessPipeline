import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def exchange_code_for_token(auth_code):
    if isinstance(auth_code, (list, tuple)):
        auth_code = auth_code[0]
    CLIENT_ID = os.getenv("inoreader_client_id")
    CLIENT_SECRET = os.getenv("inoreader_key")
    REDIRECT_URI = os.getenv("redirect_uri") 
    TOKEN_URL = os.getenv("token_url")  
    data = {
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code == 200:
        token_data = response.json()
        return token_data
    else:
        logger.error("Error exchanging code for token: %s", response.text)
        return None

