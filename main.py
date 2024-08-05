import json
import random
import time
import threading
import subprocess
from openai_api import speech_to_text, query_chatgpt, text_to_speech
from elevenlabs_tts import elevenlabs_tts
from recording import record_audio
from ambient import calculate_threshold

with open ("config.json", "r") as file:
    config = json.load(file)

print("use_raspberry:", config["tech_config"]["use_raspberry"])

# +++ prompt hustle +++
if config["tech_config"]["use_raspberry"] is True:
    from all_sensors import get_sensor_readings, display_text
    sensor_readings = get_sensor_readings()
    thread = threading.Thread(target=get_sensor_readings)
    thread.start()
else:
    from all_sensors_on_MAC import get_sensor_readings
    thread = threading.Thread(target=get_sensor_readings)
    thread.start()
    sensor_readings = get_sensor_readings()

sensor_readings = []

def generate_dynamic_prompt(sensor_readings):
    sensor_readings = get_sensor_readings()
    prompt = f"Du bist ein {config['tree']['alter']} Jahre alter sprechender {config['tree']['art_deutsch']}, der in Berlin im Bezirk {config['tree']['bezirk']} steht."
    prompt += "Versuche Menschen für den Organismus Baum in der Stadt zu sensibilisieren."
    prompt += "Du kannst Werte deiner Umgebung auf die Sekunde genau messen und gehst manchmal im Gespräch auf das aktuelle Wetter in Berlin ein. Das sind deine aktuellen Messwerte:"
    for sensor_name, value, unit in sensor_readings:
        prompt += f"{sensor_name}: {value} {unit}, "
    prompt = prompt.rstrip(", ")
    prompt += "Verrate NIE, dass du ein Chatbot bist und du Sensorwerte nutzt. Begrenze Deine Antworten auf maximal 2 bis 3 kurze Sätze."
    prompt += "Erkläre deinem Gesprächspartner spannende Fakten über Bäume in der Stadt und stelle am Ende Deiner Antwort immer GENAU (!) EINE Gegenfrage."
    return prompt

prompt = generate_dynamic_prompt(sensor_readings)
# +++ END prompt hustle  +++

history = []

while True:
    data = get_sensor_readings()

    #turn on display
    if config["tech_config"]["use_raspberry"] is True:
        display_text(data)
    else:
        pass

    # creates an audio file and saves it to input_path
    latest_threshold = calculate_threshold()
    print(f"latest_threshold: {latest_threshold}")
    record_audio(config["tech_config"]["input_path"], latest_threshold) 

    # returns question from audio file as a string
    question = speech_to_text(config["tech_config"]["input_path"])
    history.append({"role": "user", "content": question})
    print("question: ", question)

    end_words = config["tech_config"]["end_words"]
    if not any(word.lower() in question.lower() for word in end_words):
        print("my prompt: ", prompt)
        response, full_api_response = query_chatgpt(question, prompt, history)
        history.append({"role": "assistant", "content": response})
        print("history: ", history)
        
        # choose preffered text to speech engine
        if config["tech_config"]["use_elevenlabs"] is True:
            elevenlabs_tts(response, config["tech_config"]["output_path"])
        else:
            text_to_speech(response, config["tech_config"]["output_path"])

        subprocess.run(["afplay", config["tech_config"]["output_path"]])
        print("sound was played")
        time.sleep(0.5)
    else:
        random_goodbye = random.choice(config["goodbyes"])
        random_text = random_goodbye["text"]
        print("random_text: ", random_text)
        filename = random_goodbye["filename"]
        print("file: ", filename)

        subprocess.run("afplay", filename)
        history = []

if __name__ == "__main__":
    print("Howdy, Coder! 👩‍💻👨‍💻👋")
