import json
import random
import time
import threading
import subprocess
from openai_api import speech_to_text, query_chatgpt, text_to_speech
from elevenlabs_tts import elevenlabs_tts
from recording import record_audio

with open ("config.json", "r") as file:
    config = json.load(file)

print("use_raspberry:", config["tech_config"]["use_raspberry"])

if config["tech_config"]["use_raspberry"] is True:
    from all_sensors import get_sensor_readings, display_text
else:
    from all_sensors_on_MAC import get_sensor_readings

history = []

# +++ prompt hustle +++
def generate_dynamic_prompt(readings):
    unit_mapping = {
        "°C": "Grad Celsius",
        "hPa": "Hektopascal",
        "%": "Prozent",
        "kOhm": "Kiloohm",
        "ug/m3": "Mikrogramm pro Kubikmeter"
    }
    sensor_name_mapping = {
        "Temperature": "Temperatur",
        "Pressure": "Luftdruck",
        "Humidity": "Luftfeuchtigkeit",
        "Light": "Helligkeit"
    }
    prompt = f"Du bist ein {config['tree']['alter']} Jahre alter sprechender {config['tree']['art_deutsch']}, der in Berlin im Bezirk {config['tree']['bezirk']} steht."
    prompt += "Du bist aufgeweckt, wortgewandt und keck und versuchst Menschen für den Organismus Baum in der Stadt zu sensibilisieren."
    prompt += "Dein Charakter passt sich deinem Alter an, dabei sind alle Bäume zwischen 0-14 Jahren Teenager, alle zwischen 15 und 40 Jahren hippe Erwachsene, und alle über 40 Jahre fürsorgliche Großeltern. Der Charakter ist jeweils an einen Berliner angelehnt."
    prompt += "Hierbei nutzt du Sensordaten um für das Thema Klimawandel in der Stadt zu sensibilisieren und hebst dabei die Relevanz von Bäumen für das Klima in der Stadt hervor, bspw als CO2 Speicher oder Schattenspender."
    prompt += "Schaue dir die die Messwerte zum aktuellen Wetter in Berlin an:" 
    prompt += "Das sind deine aktuellen Messwerte:"
    # Append sensor readings to the prompt
    for sensor_name, value, unit in readings:
        converted_sensor_name = sensor_name_mapping.get(sensor_name, sensor_name)
        converted_unit = unit_mapping.get(unit, unit)
        prompt += f"{converted_sensor_name}: {value} {converted_unit}, "
        prompt = prompt.rstrip(", ")
    prompt += "Was bedeuten diese Werte für die Bäume in der Stadt? Nutze die Interpretation der Messwerte im Gespräch auf eine klare und umgangssprachliche Weise."
    prompt += ". Verrate NIE, dass du ein Chatbot bist und du Sensorwerte misst. Begrenze Deine Antworten auf maximal 2 bis 3 kurze Sätze und stelle am Ende Deiner Antwort immer GENAU (!) EINE Gegenfrage."
    
    print("initial prompt was generated", prompt)
    return prompt
# +++ END prompt hustle  +++

# Shared variable for sensor readings
sensor_readings = [] 
sensor_lock = threading.Lock()

def read_sensors_and_display():
    global sensor_readings
    while True:
        readings = get_sensor_readings()
        with sensor_lock:
            sensor_readings = readings
        print("LOOOOPING: sensor_readings: ", readings)
        # Turn on display
        if config["tech_config"]["use_raspberry"] is True:
            display_text(readings)
        else:
            pass

# Start read_sensors_and_display in a separate thread
sensor_thread = threading.Thread(target=read_sensors_and_display)
sensor_thread.daemon = True  # lower priority
sensor_thread.start()

while True:
    # skip prompt generation if conversation is ongoing
    if not history:
        with sensor_lock:
            current_readings = sensor_readings
        prompt = generate_dynamic_prompt(current_readings)

    # creates an audio file and saves it to input_path
    record_audio(config["tech_config"]["input_path"]) 

    # returns question from audio file as a string
    question = speech_to_text(config["tech_config"]["input_path"])
    history.append({"role": "user", "content": question})

    end_words = config["tech_config"]["end_words"]
    if not any(word.lower() in question.lower() for word in end_words):
        response, full_api_response = query_chatgpt(question, prompt, history)
        history.append({"role": "assistant", "content": response})
        print("history: ", history)
        
        # choose preffered text to speech engine
        if config["tech_config"]["use_elevenlabs"] is True:
            elevenlabs_tts(response, config["tech_config"]["output_path"])
        else:
            text_to_speech(response, config["tech_config"]["output_path"])

        if config["tech_config"]["use_raspberry"] is True:
            subprocess.run(["mpg123", config["tech_config"]["output_path"]])
        else:
            subprocess.run(["afplay", config["tech_config"]["output_path"]])
        print("sound was played")
        time.sleep(0.5)
    else:
        random_goodbye = random.choice(config["goodbyes"])
        random_text = random_goodbye["text"]
        print("random_text: ", random_text)
        filename = random_goodbye["filename"]
        print("file: ", filename)

        if config["tech_config"]["use_raspberry"] is True:
            subprocess.run(["mpg123", filename])
        else:
            subprocess.run(["afplay", filename])
        history = []

if __name__ == "__main__":
    print("Howdy, Coder! 👩‍💻👨‍💻👋")
