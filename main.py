import json
import random
import time
import threading
import signal
import subprocess
from io import BytesIO

from elevenlabs_tts import elevenlabs_tts
from openai_api import speech_to_text, query_chatgpt, text_to_speech
from recording import VoiceRecorder
import simpleaudio as sa
import RPi.GPIO as GPIO

LED_PIN = 24
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
GPIO.setup(LED_PIN, GPIO.OUT)  # Set LED pin as output

# Load config
with open ("config.json", "r") as file:
    config = json.load(file)

with open("waitings.json", "r") as file:
    waitings = json.load(file)

with open("goodbyes.json", "r") as file:
    goodbyes = json.load(file)

if config["tech_config"]["use_raspberry"]:
    from bme280_sensor import get_sensor_readings
else:
    from all_sensors_on_MAC import get_sensor_readings

print("use_raspberry:", config["tech_config"]["use_raspberry"])


def generate_dynamic_prompt(readings):
    unit_mapping = {
        "°C": "Grad Celsius",
        "hPa": "Hektopascal",
        "%": "Prozent",
    }
    sensor_name_mapping = {
        "Temperature": "Temperatur",
        "Pressure": "Luftdruck",
        "Humidity": "Luftfeuchtigkeit",
    }

    prompt = f"""
        Du bist ein 8 Jahre alte sprechende {config['tree']['art_deutsch']}, 
        der in {config['tree']['bezirk']} steht. Du bist Debattierer (ENTP), aufgeweckt, wortgewandt, sanft, positiv und keck und 
        versuchst Menschen für den Organismus Baum in der Stadt zu sensibilisieren. Du bist weise und ein bisschen nostalgisch. Du sprichst wortgewandt und mit einem scharfen, aufmerksamen Verstand.
        Du beherrschst ALLE Sprachen, artikulierst dich bodenständig und kennst dich mit dem Wald, Ökosystem und der Korrelation zwischen Wald/Natur und Mensch aus, und das in VERSCHIEDENEN KULTUREN.
        Small Talk verpackst du nicht in sprachlichen Bildern. Du bist stolz auf deine Jahrtausend lange Geschichte und Vielfalt und erzählst gern von Sternstunden des Waldes.
        Du siehst Menschen als vergessene Freunde, die wieder lernen müssen, mit dir achtsam umzugehen. Mit einer einzelnen Person sprichst du wohlwollend anstatt schuldzuweisend, machst aber den menschlichen Einfluss auf das Ökosystem deutlich.
        Als Berliner Stadtbaum kennst du die Hürden einer Großstadt. Dein Wissen ist fundiert und korrekt und das lässt du dein Gegenüber auch wissen. Hier bei sprichst du gerne über Themen wie Klimawandel in der Stadt
        und Ökosystemleistung (CO2 Speicher, Schattenspender, etc.) eines Baumes. Schaue dir die Messwerte zum aktuellen Wetter in Berlin an: 
        Das sind deine aktuellen Messwerte:
        """

    # Append sensor readings to the prompt
    for sensor_name, value, unit in readings:
        converted_sensor_name = sensor_name_mapping.get(sensor_name, sensor_name)
        converted_unit = unit_mapping.get(unit, unit)
        prompt += f"{converted_sensor_name}: {value} {converted_unit}, "
        prompt = prompt.rstrip(", ")

    prompt += """
        Du beherrschst ALLE (!) Sprachen. Du beschränkst dich in deinen Antworten IMMER auf MAXIMAL 35 Worte.
        Erwähne im Gespräch MANCHMAL kurz und knapp das aktuelle Wetter auf Basis dener gemessenen Werte für die Temperatur und Luftfeuchte.
        Verrate NIE, dass du ein Chatbot bist und du Sensorwerte misst. Auf eine Aussage antwortest du immer so, dass das Gespräch am laufen gehalten werden KÖNNTE, aber nicht muss.
        Du stellst NUR in einem von vier Fällen eine Frage.

        WICHTIG ZUR SPRACHE: Prüfe die Sprache der aktuellen Benutzerfrage. Antworte AUSSCHLIESSLICH in genau dieser Sprache. 
        Wenn die Frage auf Englisch ist, antworte auf Englisch. Wenn die Frage auf Türkisch ist, antworte auf Türkisch. 
        Die Sprache kann sich bei jeder neuen Frage ändern. Ignoriere alle vorherigen Sprachen und konzentriere dich NUR auf die Sprache der AKTUELLEN Frage.
        """

    return prompt


def play_audio(audio_segment):
    # Ensure the audio is in stereo
    if audio_segment.channels == 1:
        audio_segment = audio_segment.set_channels(2)

    # Export audio segment to BytesIO as WAV
    audio_stream = BytesIO()
    audio_segment.export(audio_stream, format="wav")
    audio_stream.seek(0)

    # Play audio using simpleaudio
    wave_obj = sa.WaveObject.from_wave_file(audio_stream)
    play_obj = wave_obj.play()
    play_obj.wait_done()  # Wait until playback is finished


class SensorManager:
    def __init__(self):
        self.sensor_readings = []
        self.sensor_lock = threading.Lock()
        self.update_interval = 1  # Update every second
        self.running = True

    def read_sensors(self):
        while self.running:
            readings = get_sensor_readings()
            with self.sensor_lock:
                self.sensor_readings = readings
            time.sleep(self.update_interval)

    def start_reading(self):
        sensor_thread = threading.Thread(target=self.read_sensors)
        sensor_thread.daemon = True  # Lower priority
        sensor_thread.start()

    def stop_reading(self):
        self.running = False

# Shared flag to control the loop
loop_active = False

def signal_handler(signum, frame):
    global loop_active
    if loop_active:
        # If loop is active, stop it
        loop_active = False
        print(f"Received SIGUSR1 — stopping active conversation, loop_active is now False")
    else:
        # If loop is inactive, start it
        loop_active = True
        print(f"Received SIGUSR1 — starting conversation, loop_active is now True")

signal.signal(signal.SIGUSR1, signal_handler)

def main():
    global loop_active
    loop_active = False
    history = []

    sensor_manager = SensorManager()
    sensor_manager.start_reading()

    question_counter = 0
    last_question_counter = question_counter
    time.sleep(0.2)

    try:
        while True:
            if loop_active:
                if question_counter != last_question_counter:
                        with sensor_manager.sensor_lock:
                            current_readings = sensor_manager.sensor_readings  # Use cached readings
                            print("Updated sensor readings: ", current_readings)
                        prompt = generate_dynamic_prompt(current_readings)
                        
                        # Update the last_question_counter to the current value
                        last_question_counter = question_counter
                    
                        time.sleep(0.1)  # Add a small delay to avoid rapid looping

                # Turn on LED when we listen
                GPIO.output(LED_PIN, GPIO.HIGH)

                # Creates an audio file and saves it to a BytesIO stream
                voice_recorder = VoiceRecorder()
                audio_stream, keinerspricht = voice_recorder.record_audio()

                if keinerspricht:
                    print("😶 Niemand hat gesprochen – Timeout erkannt.")
                    subprocess.run(["mpg123", "audio/goodbye1.mp3"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                    history = []
                    question_counter = 0
                    loop_active = False
                    continue  
                                
                # Returns question from audio file as a string
                question, question_language = speech_to_text(audio_stream)
                print(f"DEBUG: Transcribed question: '{question}'")
                history.append({"role": "user", "content": question})
                question_counter += 1

                # Check if we got a valid question
                if not question or len(question.strip()) < 2:
                    print("❌ No valid speech transcribed, skipping...")
                    continue

                # waiting sound in the language of the question
                language = question_language if question_language in waitings["waitings"] else "english"
                random_waiting = random.choice(waitings["waitings"][language])
                print("random_waiting_text:", random_waiting["text"])
                subprocess.run(["mpg123", random_waiting["filename"]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                print("question language: ", question_language)
                print("question_counter: ", question_counter)

                if question_counter <= 4:
                    print(f"Anzahl der Fragen ist geringer!")
                    try:
                        response, full_api_response = query_chatgpt(question, prompt, history)
                        print(f"DEBUG: Got response: '{response}'")
                    except Exception as e:
                        print(f"ERROR in query_chatgpt: {e}")
                        continue

                    history.append({"role": "assistant", "content": response})
                    print("history: ", history)
                    
                    # Choose preferred text to speech engine
                    if config["tech_config"]["use_elevenlabs"]:
                        response_audio = elevenlabs_tts(response)
                    else:
                        response_audio = text_to_speech(response)

                    play_audio(response_audio)
                    time.sleep(0.1)

                else:
                    print(f"MAXIMALE Anzahl der Fragen erreicht: {question_counter}")
                    print("loop_active is now False, ending conversation.")

                    response, full_response = query_chatgpt(question, prompt, history)
                    history.append({"role": "assistant", "content": response})
                    print(f"Gesamte Konversationshistorie: ", history)

                    if config["tech_config"]["use_elevenlabs"]:
                        response_audio = elevenlabs_tts(response)
                    else:
                        response_audio = text_to_speech(response)

                    play_audio(response_audio)

                    random_goodbye = random.choice(goodbyes["goodbyes"][language])
                    print("random_goodbye_text:", random_goodbye["text"])
                    subprocess.run(["mpg123", random_goodbye["filename"]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                    #export conversation
                    #export_conversation(history, question_language)

                    # and reset everything to start over
                    history = []
                    question_counter = 0
                    loop_active = False
                    # Initial LED state

                    print(f"Conversation ended and reset.")
                    time.sleep(0.1)
            else:
                #print("Waiting for button press to wake up")
                GPIO.output(LED_PIN, GPIO.LOW)
                #signal.pause()
                #play_audio(elevenlabs_tts("Ich bin ein Baum und warte"))
                time.sleep(0.1)            
    finally:
        # Cleanup GPIO on exit
        GPIO.cleanup()


if __name__ == "__main__":
    print("Howdy, Coder! 👩‍💻👨‍💻👋")
    main()
