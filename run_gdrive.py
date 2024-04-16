from pydub import AudioSegment
import openai
import os
import io
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import argparse
import dotenv
import tqdm 

parser = argparse.ArgumentParser()

parser.add_argument("--audio_dir", default="/Learning/Audio To Be Transcribed")
parser.add_argument("--output_dir", default="/Learning/Audio Transcriptions")

args = parser.parse_args()

def download_file(service, file_id):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    return fh

def get_folder_id_by_path(service, path):
    if path == '/':
        return 'root'
    elif not path.startswith('/'):
        raise ValueError("Path must start with '/'.")

    folder_id = 'root'
    parts = path.strip('/').split('/')
    
    for part in parts:
        response = service.files().list(q=f"mimeType='application/vnd.google-apps.folder' and name='{part}' and '{folder_id}' in parents and trashed=false",
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name)').execute()
        files = response.get('files', [])
        
        if not files:
            raise ValueError(f"No folder with name '{part}'")
        folder_id = files[0]['id']
        
    return folder_id

def transcribe_audio_chunks(chunk_file_paths, service, transcriptor, output_dir, file):
    output_text_file = file['name'].replace('.mp3', '.txt')
    output_text_path = os.path.join("data/processed", output_text_file)

    with open(output_text_path, "w") as f:
        for chunk_path in chunk_file_paths:
            with open(chunk_path, "rb") as audio_file:
                transcription = transcriptor.create(
                    model="whisper-1",
                    file=audio_file
                )
                f.write(transcription.text + '\n\n')

    output_folder_id = get_folder_id_by_path(service, output_dir)
    file_metadata = {'name': output_text_file, 'parents': [output_folder_id]}
    media = MediaIoBaseUpload(io.FileIO(output_text_path, 'rb'), mimetype='text/plain')
    service.files().create(body=file_metadata, media_body=media).execute()

def chunk_audio_file(file_path, chunk_length_ms=600000):  # 10 minutes
    audio = AudioSegment.from_file(file_path)
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunk_path = os.path.join(f"{file_path.replace(".mp3", "")}_chunks", f"chunk{i//chunk_length_ms}.mp3")
        chunk = audio[i:i+chunk_length_ms]
        chunk.export(chunk_path, format="mp3")
        chunks.append(chunk_path)
    return chunks

def get_audio_files_from_folder(service, audio_dir):
    folder_id = get_folder_id_by_path(service, audio_dir)
    query = f"'{folder_id}' in parents and trashed=false"
    files = service.files().list(q=query, fields="nextPageToken, files(id, name, mimeType)").execute()
    items = files.get('files', [])
    return items



def load_gdrive_api_service():
    token_path = os.environ.get("GDRIVE_TOKEN_PATH")
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    service = build('drive', 'v3', credentials=creds)
    return service

def load_transcriptor():
    client = openai.OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    transcriptor = client.audio.transcriptions
    return transcriptor

def save_local_copy(file_io, path):
    path = os.path.join(path)  # Specify your directory path
    with open(path, 'wb') as audio_file:
        audio_file.write(file_io.getvalue())
    return path



def main(args):
    print(f"\nLoad audio files from:      {args.audio_dir}")
    print(f"\nWriting transcriptions to:  {args.output_dir}")

    dotenv.load_dotenv()


    client = openai.OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    service = load_gdrive_api_service()
    transcriptor = load_transcriptor()
    files = get_audio_files_from_folder(service=service, audio_dir=args.audio_dir)
    progress_bar = tqdm.tqdm(files, desc="Files to be processed")

    for file in files:
        print(f'\nname:{file["name"]}, id:{file["id"]}, mimeType:{[file["mimeType"]]}')
        
        file_io = download_file(service, file['id'])
        temp_path = os.path.join("data/raw", file["name"])
        save_local_copy(file_io=file_io, path=temp_path)
        chunk_file_paths = chunk_audio_file(temp_path)
        

        with open(temp_path, "rb") as f:
            transcribe_audio_chunks(chunk_file_paths, service, transcriptor, args.output_dir, file)

        
        progress_bar.update(1)

if __name__ == "__main__":
    main(args)
