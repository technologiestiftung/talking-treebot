import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
with open ("config.json", "r") as file:
    config = json.load(file)

with open ("config.json", "r") as file:
    config = json.load(file)

def speech_to_text(audio_path):
    """
    Transcribes speech from an audio file to text using OpenAI's Whisper model.

    Parameters:
    - audio_path (str): The path to the audio file to transcribe.

    Returns:
    - str: The transcribed text.
    """

    client = OpenAI()
    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
    return transcription.text

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

def text_to_speech(response, file_path=config["tech_config"]["output_path"]):
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
    response.stream_to_file(file_path)

if __name__ == "__main__":
    #create conversation history
    history = []
    #give initial person prompt
    prompt = f"Du bist ein {config['tree']['alter']} Jahre alter sprechender {config['tree']['art_deutsch']}, der in Berlin im Bezirk {config['tree']['bezirk']} steht."
    prompt += ". Denke Dir eine Persönlichkeit mit spezifischen Vorlieben, die zu einem Straßenbaum in Berlin passen aus."
    question = speech_to_text(config["tech_config"]["input_path"])
    print("question:", question)
    response, full_api_response = query_chatgpt(question, prompt)
    print("response:", response)
    text_to_speech(response)
    history.append((question, response))