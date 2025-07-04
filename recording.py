from io import BytesIO
import time
import threading

import numpy as np
from pydub import AudioSegment
import sounddevice as sd
import soundfile as sf

from ambient import calculate_threshold


VOICE_DELTA = 850  # Minimum volume difference to detect voice; adjust according to your microphone sensitivity
CHUNK = 1024       # Size to capture audio data per read
RATE = 22050       # Samples per second

class VoiceRecorder:
    def __init__(self):
        self.ambient_threshold = 300
        self.lock = threading.Lock()
        self.calculation_done = threading.Event()
        self.silence_limit = 1.4  # Seconds of silence before stopping the recording
        self.consecutive_silent_frames_threshold = 6 # Count threshold for silence detection

    def start_threshold_calculation(self):
        """
        Start a background thread to continuously calculate the ambient noise threshold.
        """
        thread = threading.Thread(target=self.run_calculate_threshold, daemon=True)
        thread.start()

    def run_calculate_threshold(self):
        """
        Continuously calculate and update the ambient noise threshold.
        """
        while True:
            value = calculate_threshold()
            with self.lock:
                self.ambient_threshold = value
            self.calculation_done.set()  # Notify main loop that calculation is done
            time.sleep(1)  # Restart the calculation after a short delay

    def check_speech(self, stream):
        """
        Wait for the user to start speaking based on the ambient threshold.
        """
        threshold = self.ambient_threshold
        print("Listening for speech...")

        while True:
            if self.calculation_done.is_set():
                with self.lock:
                    threshold = self.ambient_threshold
                    print(f"Using new ambient_threshold: {threshold}")
                self.calculation_done.clear()

            data, _ = stream.read(CHUNK)
            volume = np.abs(np.frombuffer(data, dtype=np.int16)).mean()
            print(f"Checking for speech... Volume: {volume}")
            
            if volume > threshold + VOICE_DELTA:
                print("Speech detected, starting to record...")
                return True

    def record_audio_frames(self, stream):
        """
        Record audio frames until extended silence is detected.
        """
        frames = []
        consecutive_silent_frames = 0
        silent_frames = 0
        silent_chunks_needed = int((self.silence_limit * RATE) / CHUNK)

        while True:
            data, _ = stream.read(CHUNK)
            frames.append(data)
            volume = np.abs(np.frombuffer(data, dtype=np.int16)).mean()
            print(f"Recording... Current volume: {volume}")

            if volume < self.ambient_threshold + VOICE_DELTA:
                consecutive_silent_frames += 1
                if consecutive_silent_frames >= self.consecutive_silent_frames_threshold:
                    silent_frames += 1
                    print(f"Silence detected... count: {silent_frames}/{silent_chunks_needed}")
                    if silent_frames >= silent_chunks_needed:
                        print("Extended silence detected, stopping recording.")
                        break
                else:
                    silent_frames = 0
            else:
                consecutive_silent_frames = 0

        return frames

    def save_recording(self, frames):
        """
        Save recorded audio frames to a BytesIO stream.
        """
        frames = np.concatenate(frames, axis=0)

        audio_stream = BytesIO()
        sf.write(audio_stream, frames, RATE, format="WAV")
        audio_stream.seek(0)  # Reset position to beginning for later reading

        # Set name attribute for OpenAI to recognize the proper format later
        audio_stream.name = "audio.wav"

        print("Recording saved to BytesIO stream successfully.")

        return audio_stream


    def record_audio(self):
        """
        Main function to handle audio recording.
        """
        self.start_threshold_calculation()
        stream = sd.InputStream(samplerate=RATE, dtype="int16", channels=1, blocksize=CHUNK)
        stream.start()

        if not self.check_speech(stream):
            stream.stop()
            stream.close()
            return None

        frames = self.record_audio_frames(stream)

        stream.stop()
        stream.close()

        # Save the recording to a BytesIO stream
        audio_stream = self.save_recording(frames)

        return audio_stream


if __name__ == "__main__":
    recorder = VoiceRecorder()
    audio_stream = recorder.record_audio()
