import os
import requests
from dotenv import load_dotenv
load_dotenv()
from src.results import output_results_excel
def get_graph_api_token(tenant_id, client_id, client_secret):
    """
    Obtains an access token for Microsoft Graph using the client credentials flow.
    
    Parameters:
      - tenant_id: Your Azure AD Tenant ID.
      - client_id: Your application's Client ID.
      - client_secret: Your application's Client Secret.
    
    Returns:
      - The access token as a string if successful, or None otherwise.
    """
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "client_id": client_id,
        "scope": "https://graph.microsoft.com/.default",
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    response = requests.post(token_url, data=data)
    if response.ok:
        token = response.json().get("access_token")
        print("Obtained Graph API token.")
        return token
    else:
        print("Failed to obtain token:", response.status_code, response.text)
        return None

def upload_file_to_onedrive(file_path, drive_id, parent_item_id, file_name, access_token):
    """
    Uploads a file to a OneDrive folder specified by the drive ID and the parent folder's item ID.
    
    Parameters:
      - file_path: Local path to the file to upload.
      - drive_id: The ID of the target drive (in this case, the News screening drive).
      - parent_item_id: The ID of the target folder (e.g., for "Output the results folder").
      - file_name: The name with which the file will be saved on OneDrive.
      - access_token: A valid Microsoft Graph API access token.
    
    Returns:
      - The JSON response from the API if the upload is successful, or None otherwise.
    """
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{parent_item_id}:/{file_name}:/content"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream"
    }
    with open(file_path, "rb") as f:
        file_data = f.read()
    
    response = requests.put(url, headers=headers, data=file_data)
    if response.status_code in (200, 201):
        print("File uploaded successfully.")
        return response.json()
    else:
        print("Failed to upload file:", response.status_code, response.text)
        return None

def main():
    # Get credentials from environment variables.
    tenant_id = os.getenv("OD_TENANT_ID")
    client_id = os.getenv("OD_CLIENT_ID")
    client_secret = os.getenv("OD_CLIENT_VALUE")
    if not (tenant_id and client_id and client_secret):
        print("Missing one or more Azure AD credential environment variables.")
        return
    
    # Obtain an access token using client credentials.
    graph_access_token = get_graph_api_token(tenant_id, client_id, client_secret)
    if not graph_access_token:
        print("Could not obtain Graph API token.")
        return

    # Define the name and path for the empty file.
    
    output_results_excel([],[],"test_results.xlsx")


if __name__ == "__main__":
    main()
