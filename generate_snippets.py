import json
from elevenlabs_tts import elevenlabs_tts  

def generate_audio_snippets(config_file):
    with open(config_file, 'r') as file:
        config = json.load(file)

    for category in ['greetings', 'waitings', 'goodbyes']:
        for item in config[category]:
            elevenlabs_tts(item['text'], item['filename'])

if __name__ == "__main__":
    generate_audio_snippets('config.json')