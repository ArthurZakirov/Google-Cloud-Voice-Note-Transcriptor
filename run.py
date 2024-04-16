import openai
import os
import dotenv
import json

dotenv.load_dotenv()

client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

audio_path = "data/raw/Reflection.mp3"
txt_output_path = "data/processed/transcription.txt"
json_output_path = "data/processed/transcription.json"


with open(audio_path, "rb") as f:
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        response_format="verbose_json",
        timestamp_granularities=["word", "segment"],
        file=f
    )

# with open(output_path, "w") as f:
#     f.write(transcription.text)

with open(json_output_path, "w") as f:
    json.dump(transcription, f)

print("Finished!")