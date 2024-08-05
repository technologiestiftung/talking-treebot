import sounddevice as sd
import numpy as np
import soundfile as sf
import time
import threading
import json
from ambient import calculate_threshold

VOICE_DELTA = 850 # Minimum volume difference to detect voice; adjust according to your microphone sensitivity
CHUNK = 1024 # size to capture audio data per read
RATE = 22050  # samples per second

# +++ multithreading +++
# Shared data and lock
ambient_threshold = 300
lock = threading.Lock()
calculation_done = threading.Event()

def run_calculate_threshold():
    global ambient_threshold
    while True:
        value = calculate_threshold()
        with lock:
            ambient_threshold = value
        calculation_done.set()  # Notify main loop that calculation is done
        time.sleep(1)  # Restart the calculation after the current one is done

threading.Thread(target=run_calculate_threshold, daemon=True).start()
# +++ END multithreading +++

def record_audio(filename):
    THRESHOLD = ambient_threshold
    SILENCE_LIMIT = 1.4  # Number of seconds of silence before stopping the recording
    # TIMEOUT_AFTER_SECONDS = 10  # Maximum recording time in seconds
    CONSECUTIVE_SILENT_FRAMES_THRESHOLD = 3  # Number of consecutive silent frames before counting one real silence frame
    IS_TIMEOUT = False

    print("threshold: ", THRESHOLD)
    # Calculate the number of silent chunks needed to reach the silence limit
    silent_chunks_needed = int((SILENCE_LIMIT * RATE) / CHUNK)
    print(f"Silence threshold in chunks: {silent_chunks_needed}")

    # Initialize sounddevice stream
    stream = sd.InputStream(samplerate=RATE, dtype='int16', channels=1, blocksize=CHUNK)
    stream.start()

    print("Listening for speech...")
    # Wait for the user to start speaking
    while True:
        # Check if the calculation is done
        if calculation_done.is_set():
        # Use the result
            with lock:
                THRESHOLD = ambient_threshold
                print(f"Using ambient_threshold: {ambient_threshold}")
            # Reset the event for the next calculation
            calculation_done.clear()

        data, _ = stream.read(CHUNK)
        data = np.frombuffer(data, dtype=np.int16)
        volume = np.abs(data).mean()
        print(f"Checking for speech... Volume: {volume}")
        print(f"Threshold: {THRESHOLD}")
        if volume > THRESHOLD + VOICE_DELTA:
            print("Speech detected, starting to record...")
            break
        # if (time.time() - start_time) >= TIMEOUT_AFTER_SECONDS:
        #     IS_TIMEOUT = True
        #     print("Timeout reached without detecting speech.")
        #     break

    # Record for the specified duration or until the user stops speaking
    frames = []
    consecutive_silent_frames = 0
    silent_frames = 0
    
    while True:
        data, _ = stream.read(CHUNK)
        data = np.frombuffer(data, dtype=np.int16)
        frames.append(data)
        volume = np.abs(data).mean()
        print(f"Recording... Current volume: {volume}")

        if volume < THRESHOLD + VOICE_DELTA:
            consecutive_silent_frames += 1
            if consecutive_silent_frames >= CONSECUTIVE_SILENT_FRAMES_THRESHOLD:
                silent_frames += 1
                print(f"Silence detected... count: {silent_frames}/{silent_chunks_needed}")
                if silent_frames >= silent_chunks_needed:
                    print("Extended silence detected, stopping recording.")
                    break
        else:
            silent_frames = 0

    stream.stop()
    stream.close()

    # Convert the frames to a single audio file
    frames = np.concatenate(frames, axis=0)
    sf.write(filename, frames, RATE)

    if IS_TIMEOUT:
        print("Recording stopped due to timeout without sufficient speech detected.")
        return False
    else:    
        print("Recording saved successfully.")
        return True


if __name__ == "__main__":
    timeout_occurred = record_audio("question.wav")
