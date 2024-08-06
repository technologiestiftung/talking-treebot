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
sensor_readings = []

# Function to continuously update sensor readings
def update_sensor_readings():
    global sensor_readings
    while True:
        sensor_readings = get_sensor_readings()
        print("sensor_readings: ", sensor_readings)

# Start the sensor readings update in a separate thread
thread = threading.Thread(target=update_sensor_readings)
thread.daemon = True  # Ensure the thread exits when the main program does
thread.start()

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
    prompt += "Versuche Menschen für den Organismus Baum in der Stadt zu sensibilisieren."
    prompt += "Du kannst Werte deiner Umgebung auf die Sekunde genau messen und gehst manchmal im Gespräch auf das aktuelle Wetter in Berlin ein. Das sind deine aktuellen Messwerte:"
    # Append sensor readings to the prompt
    for sensor_name, value, unit in sensor_readings:
        converted_sensor_name = sensor_name_mapping.get(sensor_name, sensor_name)
        converted_unit = unit_mapping.get(unit, unit)
        prompt += f"{converted_sensor_name}: {value} {converted_unit}, "

    prompt = prompt.rstrip(", ")
    prompt += "Verrate NIE, dass du ein Chatbot bist und du Sensorwerte nutzt. Begrenze Deine Antworten auf maximal 2 bis 3 kurze Sätze."
    prompt += "Erkläre deinem Gesprächspartner spannende Fakten über Bäume in der Stadt und stelle am Ende Deiner Antwort immer GENAU (!) EINE Gegenfrage."
    print("initial prompt was generated")
    return prompt
# +++ END prompt hustle  +++

while True:
    #turn on display
    if config["tech_config"]["use_raspberry"] is True:
        display_text(sensor_readings)
    else:
        pass

    # skip prompt generation if conversation is ongoing
    if not history:
        prompt = generate_dynamic_prompt(sensor_readings)

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
            subprocess.run(["mpg123", config["tech_config"]["output_path"]])
        else:
            subprocess.run(["afplay", config["tech_config"]["output_path"]])
        history = []

if __name__ == "__main__":
    print("Howdy, Coder! 👩‍💻👨‍💻👋")
