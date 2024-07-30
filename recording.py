import sounddevice as sd
import numpy as np
import soundfile as sf
import time

def record_audio(filename):
    CHUNK = 1024
    RATE = 22050  # samples per second
    THRESHOLD = 300  # Adjust  value to set  sensitivity of voice detection // 300 for MAC
    SILENCE_LIMIT = 1.2  # Number of seconds of silence before stopping the recording
    TIMEOUT_AFTER_SECONDS = 10  # Maximum recording time in seconds
    CONSECUTIVE_SILENT_FRAMES_THRESHOLD = 3  # Number of consecutive silent frames before counting one real silence frame
    IS_TIMEOUT = False

    # Calculate the number of silent chunks needed to reach the silence limit
    silent_chunks_needed = int((SILENCE_LIMIT * RATE) / CHUNK)
    print(f"Silence threshold in chunks: {silent_chunks_needed}")

    # Initialize sounddevice stream
    stream = sd.InputStream(samplerate=RATE, dtype='int16', channels=1, blocksize=CHUNK)
    stream.start()

    print("Listening for speech...")
    # Wait for the user to start speaking
    start_time = time.time()
    while True:
        data, _ = stream.read(CHUNK)
        data = np.frombuffer(data, dtype=np.int16)
        volume = np.abs(data).mean()
        print(f"Checking for speech... Volume: {volume}")
        if volume > THRESHOLD:
            print("Speech detected, starting to record...")
            break
        if (time.time() - start_time) >= TIMEOUT_AFTER_SECONDS:
            IS_TIMEOUT = Trueç
            print("Timeout reached without detecting speech.")
            break

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

        if volume < THRESHOLD:
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
