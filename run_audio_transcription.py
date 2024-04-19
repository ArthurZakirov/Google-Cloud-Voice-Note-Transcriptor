import openai
import os
import io
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import argparse
import dotenv
import tqdm

from src.drive_io.drive_utils import get_audio_files_from_folder, load_service
from src.drive_io.drive_sync import download_file, upload_txt_files_to_folder
from src.audio_transcription.transcribe import (
    load_transcriptor,
    transcribe_audio_chunks,
)
from src.audio_transcription.audio_utils import save_local_copy, chunk_audio_file

parser = argparse.ArgumentParser()

parser.add_argument("--audio_dir", default="/Learning/Audio To Be Transcribed")
parser.add_argument("--output_dir", default="/Learning/Audio Transcriptions")
parser.add_argument("--temp_audio_chunk_dir", default="data/temp_audio_chunks")
parser.add_argument("--temp_transcription_dir", default="data/temp_transcriptions")


args = parser.parse_args()


def main(args):
    dotenv.load_dotenv()
    service = load_service()
    transcriptor = load_transcriptor()
    files = get_audio_files_from_folder(service=service, audio_dir=args.audio_dir)
    progress_bar = tqdm.tqdm(files, desc="Files to be processed")

    for file in files:
        file_io = download_file(service, file["id"])
        temp_path = os.path.join(args.temp_audio_chunk_dir, file["name"])
        save_local_copy(file_io=file_io, path=temp_path)
        chunk_file_paths = chunk_audio_file(temp_path)

        text_file = file["name"].replace(".mp3", ".txt")
        temp_text_path = os.path.join(args.temp_transcription_dir, text_file)

        transcribe_audio_chunks(chunk_file_paths, temp_text_path, transcriptor)

        upload_txt_files_to_folder(
            service, args.output_dir, args.temp_transcription_dir, text_file
        )
        progress_bar.update(1)


if __name__ == "__main__":
    main(args)
