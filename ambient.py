import numpy as np
import sounddevice as sd

CHUNK = 1024 # size to capture audio data per read
RATE = 22050  # samples per second

def calculate_threshold(duration=10, fs=22050, buffer_value=10):
    print("Recording ambient noise...")
    # Create a buffer to hold the recorded audio data
    ambient_data = np.zeros(int(duration * fs), dtype=np.int16)
    with sd.InputStream(samplerate=fs, dtype='int16', channels=1, blocksize=CHUNK) as stream:
        # Read audio data in chunks and store it in the buffer
        for i in range(0, len(ambient_data), CHUNK):
            data, _ = stream.read(CHUNK)
            # Adjust the size of the last chunk to fit the remaining space
            if i + CHUNK > len(ambient_data):
                # Calculate remaining space
                remaining = len(ambient_data) - i
                # Resize the data to fit the remaining space
                ambient_data[i:i+remaining] = np.frombuffer(data, dtype=np.int16)[:remaining]
            else:
                ambient_data[i:i+CHUNK] = np.frombuffer(data, dtype=np.int16)

    # Calculate ambient noise volume
    ambient_volume = np.abs(ambient_data).mean()

    print("Finished recording ambient noise...")
    return ambient_volume + buffer_value

if __name__ == "__main__":
    print(calculate_threshold())