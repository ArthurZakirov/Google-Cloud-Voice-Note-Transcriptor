import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def get_audio_files_from_folder(service, audio_dir):
    """
    Retrieves a list of audio files from a specified folder in Google Drive.

    Args:
        service: The Google Drive API service object.
        audio_dir (str): The path of the audio folder in Google Drive.

    Returns:
        list: A list of all audio files in the specified folder, each represented as a dictionary with 'id', 'name', and 'mimeType' fields.
    """
    folder_id = get_folder_id_by_path(service, audio_dir)
    query = f"'{folder_id}' in parents and trashed=false"
    items = []  # Initialize an empty list to store all files
    page_token = None  # Start with no page token

    while True:
        response = (
            service.files()
            .list(
                q=query,
                fields="nextPageToken, files(id, name, mimeType)",
                pageToken=page_token,
                pageSize=100,
            )  # Can specify pageSize, default is 100
            .execute()
        )

        items.extend(
            response.get("files", [])
        )  # Add current batch of files to the list

        page_token = response.get("nextPageToken", None)  # Update the page_token
        if not page_token:  # If no more pages, break the loop
            break

    return items


def get_folder_id_by_path(service, path):
    """
    Retrieves the folder ID in Google Drive based on the given path.

    Args:
        service: The Google Drive service object.
        path (str): The path of the folder in Google Drive.

    Returns:
        str: The ID of the folder in Google Drive.

    Raises:
        ValueError: If the path does not start with '/' or if no folder with the given name is found.
    """
    if path == "/":
        return "root"
    elif not path.startswith("/"):
        raise ValueError("Path must start with '/'.")

    folder_id = "root"
    parts = path.strip("/").split("/")

    for part in parts:
        response = (
            service.files()
            .list(
                q=f"mimeType='application/vnd.google-apps.folder' and name='{part}' and '{folder_id}' in parents and trashed=false",
                spaces="drive",
                fields="nextPageToken, files(id, name)",
            )
            .execute()
        )
        files = response.get("files", [])

        if not files:
            raise ValueError(f"No folder with name '{part}'")
        folder_id = files[0]["id"]

    return folder_id


def load_service():
    """
    Loads the Google Drive API service using the provided credentials.

    Returns:
        service (googleapiclient.discovery.Resource): The Google Drive API service.
    """
    token_path = os.environ.get("DRIVE_TOKEN_PATH")
    SCOPES = ["https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    service = build("drive", "v3", credentials=creds)
    return service
