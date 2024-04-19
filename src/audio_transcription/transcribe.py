import os
import openai


def load_transcriptor():
    """
    Load the OpenAI transcriptor client.

    Returns:
        The OpenAI transcriptor client.
    """
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    transcriptor = client.audio.transcriptions
    return transcriptor


def transcribe_audio_chunks(chunk_file_paths, output_text_path, transcriptor):
    """
    Transcribe audio chunks and write the transcriptions to a text file.

    Args:
        chunk_file_paths (list): List of paths to audio chunk files.
        output_text_path (str): Path to the output text file.
        transcriptor: The OpenAI transcriptor client.

    Returns:
        None
    """
    if not os.path.exists(os.path.dirname(output_text_path)):
        os.makedirs(os.path.dirname(output_text_path))

    with open(output_text_path, "w") as f:
        for chunk_path in chunk_file_paths:
            with open(chunk_path, "rb") as audio_file:
                transcription = transcriptor.create(model="whisper-1", file=audio_file)
                f.write(transcription.text + "\n\n")
