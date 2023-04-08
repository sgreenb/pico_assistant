import requests
import json
from pydub import AudioSegment
from pydub.playback import play
import io

elevenlabs_key = open("elevenlabs_key.txt", "r").read().strip("\n")  # get api key from text file

def elevenlabs_tts(text, stability = 0.6, similarity_boost = 0.75):
    url = 'https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL/stream'
    headers = {
        'accept': '*/*',
        'xi-api-key': elevenlabs_key,
        'Content-Type': 'application/json'
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)

    if response.status_code == 200:
        return response.content
    else:
        print(f"Request failed with status code {response.status_code}")
        return None

def play_audio_content(audio_content):
    audio = AudioSegment.from_file(io.BytesIO(audio_content), format="mp3")
    play(audio)