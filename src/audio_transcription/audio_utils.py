import os
from pydub import AudioSegment


def save_local_copy(file_io, path):
    """
    Saves a local copy of the audio file.

    Args:
        file_io (io.BytesIO): The audio file as a BytesIO object.
        path (str): The directory path to save the file.

    Returns:
        str: The path of the saved file.
    """
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    with open(path, "wb") as audio_file:
        audio_file.write(file_io.getvalue())
    return path


def chunk_audio_file(file_path, chunk_length_ms=600000):
    """
    Splits an audio file into chunks of specified length.

    Args:
        file_path (str): The path of the audio file.
        chunk_length_ms (int): The length of each chunk in milliseconds. Default is 10 minutes (600000 ms).

    Returns:
        list: A list of paths to the generated audio chunks.
    """
    audio = AudioSegment.from_file(file_path)
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunk_dir = f"{file_path.replace('.mp3', '')}_chunks"
        if not os.path.exists(chunk_dir):
            os.makedirs(chunk_dir)

        chunk_file = f"chunk{i//chunk_length_ms}.mp3"
        chunk_path = os.path.join(chunk_dir, chunk_file)
        chunk = audio[i : i + chunk_length_ms]
        chunk.export(chunk_path, format="mp3")
        chunks.append(chunk_path)
    return chunks
