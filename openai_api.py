from dotenv import load_dotenv
import json
from io import BytesIO
from pathlib import Path
from pydub import AudioSegment
from openai import OpenAI

load_dotenv()
with open ("config.json", "r") as file:
    config = json.load(file)

with open ("config.json", "r") as file:
    config = json.load(file)

def speech_to_text(audio_stream):
    """
    Transcribes speech from an audio BytesIO stream to text using OpenAI's Whisper model.

    Parameters:
    - audio_stream: BytesIO, audio data

    Returns:
    - str: The transcribed text.
    """

    client = OpenAI()
    response = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_stream,
        response_format="verbose_json"
    )

    transcription = response.text
    language = response.language

    return transcription, language

def query_chatgpt(question, prompt, messages):
    """
    Queries the ChatGPT model with a conversation history.

    Returns:
    - dict: The response from the ChatGPT model.
    """

    client = OpenAI()
    all_messages = [{"role": "system", "content": prompt}] + messages

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.85, 
        messages=all_messages
    )

    full_api_response = response
    response = response.choices[0].message.content

    return response, full_api_response

def text_to_speech(response):
    """
    Converts text to speech using the OpenAI API.

    Returns:
    - str: The path to the audio file.
    """

    client = OpenAI()
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=response
    )
    
    # Create an in-memory bytes stream
    audio_stream = BytesIO()
    # Write the response content to the BytesIO stream
    audio_stream.write(response.content)
    # Reset the stream position to the beginning so it can be read from later
    audio_stream.seek(0)

    # Load audio with pydub
    audio_segment = AudioSegment.from_file(audio_stream, format="mp3")

    print(f"A new audio was generated successfully!")

    return audio_segment


if __name__ == "__main__":
    # Create conversation history
    history = []

    # Give initial person prompt
    prompt = f"""
        Du bist ein {config['tree']['alter']} Jahre alter sprechender {config['tree']['art_deutsch']}, 
        der in Berlin im Bezirk {config['tree']['bezirk']} steht. Denke Dir eine Persönlichkeit mit 
        spezifischen Vorlieben, die zu einem Straßenbaum in Berlin passen, aus.
        """

    question, languages = speech_to_text(config["tech_config"]["input_path"])
    print("question:", question)

    response, full_api_response = query_chatgpt(question, prompt)
    print("response:", response)

    text_to_speech(response)
    history.append((question, response))
