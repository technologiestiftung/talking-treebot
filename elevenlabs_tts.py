from dotenv import load_dotenv
from io import BytesIO
import os

from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def elevenlabs_tts(transcription):
    response = client.text_to_speech.convert(
        voice_id="KqY0pr2VOkd9SVIHMnwM", # Matilda
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",  # Use MP3 format with 22.05kHz sample rate at 32kbps
        text=transcription,
        model_id="eleven_turbo_v2_5", # faster than eleven_multilingual_v2pport
        voice_settings=VoiceSettings(
            stability=0.8,
            similarity_boost=1.0,
            style=0.6,
            use_speaker_boost=True,
        ),
    )

    # Use BytesIO to store audio data in memory
    audio_data = BytesIO()
    for chunk in response:
        if chunk:
            audio_data.write(chunk)
    audio_data.seek(0)  # Reset the stream position to the beginning

    # Load audio with pydub
    audio_segment = AudioSegment.from_file(audio_data, format="mp3")

    print(f"A new audio was generated successfully!")

    return audio_segment
