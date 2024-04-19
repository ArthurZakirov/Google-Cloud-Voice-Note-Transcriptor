import io
import os
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from .drive_utils import get_folder_id_by_path


def download_file(service, file_id):
    """
    Downloads a file from Google Drive.

    Args:
        service: The Google Drive service object.
        file_id: The ID of the file to download.

    Returns:
        The downloaded file as a BytesIO object.
    """
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return fh


def upload_txt_files_to_folder(service, output_dir, txt_dir, text_file):
    """
    Uploads a text file to a specific folder in Google Drive.

    Args:
        service (googleapiclient.discovery.Resource): The Google Drive API service object.
        output_dir (str): The path to the output directory where the file is located.
        txt_dir (str): The path to the directory where the text file is located.
        text_file (str): The name of the text file to be uploaded.

    Returns:
        None
    """
    output_folder_id = get_folder_id_by_path(service, output_dir)
    file_metadata = {"name": text_file, "parents": [output_folder_id]}
    text_path = os.path.join(txt_dir, text_file)
    media = MediaIoBaseUpload(io.FileIO(text_path, "rb"), mimetype="text/plain")
    service.files().create(body=file_metadata, media_body=media).execute()
