import requests
import json

elevenlabs_key = open("elevenlabs_key.txt", "r").read().strip("\n")  # get api key from text file

def elevenlabs_tts(text, output_file, stability = 0.6, similarity_boost = 0.75):
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

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        # Save the audio file
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print(f"Audio file saved to {output_file}")
    else:
        print(f"Request failed with status code {response.status_code}")

# Example usage
text = "I am Pico, an AI assistant!"
output_file = "./speech_files/output.mp3"
elevenlabs_tts(text, output_file)
