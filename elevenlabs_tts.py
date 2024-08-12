import os
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)

def elevenlabs_tts(transcription, filepath):
    response = client.text_to_speech.convert(
        voice_id="KqY0pr2VOkd9SVIHMnwM", # Matilda
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",  # Use MP3 format with 22.05kHz sample rate at 32kbps
        text=transcription,
        model_id="eleven_multilingual_v2", # use the eleven_turbo_v2 model for low latency, use eleven_multilingual_v2 for multilingual support
        voice_settings=VoiceSettings(
            stability=0.8,
            similarity_boost=1.0,
            style=0.6,
            use_speaker_boost=True,
        ),
    )

    # Writing the audio to a file
    with open(filepath, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"{filepath}: A new audio file was saved successfully!")

    # Return the path of the saved audio file
    return filepath

if __name__ == "__main__":
    transcription = "Als sprechender Spitzahorn hier in Berlin ist es mir wichtig, Menschen für den Organismus Baum zu sensibilisieren. Bäume kommunizieren untereinander über Wurzelsysteme und chemische Signale, um sich vor Gefahren zu warnen oder Nährstoffe auszutauschen. Wie stark fühlt sich die Luftqualität für euch an in Bezug auf die aktuellen Messwerte?"
    elevenlabs_tts(transcription, "answer.mp3")
