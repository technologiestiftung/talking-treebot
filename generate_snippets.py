import json
from elevenlabs_tts import elevenlabs_tts_to_mp3 

def generate_audio_snippets(config_file):
    with open(config_file, 'r') as file:
        waitings = json.load(file)

    for category in waitings:
        for item in waitings[category]:
            elevenlabs_tts_to_mp3(item['text'], item['filename'])

if __name__ == "__main__":
    generate_audio_snippets('waitings.json')