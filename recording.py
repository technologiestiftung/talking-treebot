from io import BytesIO
import time
import threading
import numpy as np
from pydub import AudioSegment
import sounddevice as sd
import soundfile as sf

from ambient import calculate_threshold

VOICE_DELTA = 850  # minimum volume difference to detect voice
CHUNK = 1024       # audio buffer size
RATE = 22050       # sampling rate

class VoiceRecorder:
    def __init__(self):
        self.ambient_threshold = 300
        self.lock = threading.Lock()
        self.calculation_done = threading.Event()
        self.silence_limit = 1.4  # seconds of silence before stopping
        self.consecutive_silent_frames_threshold = 6  # silence frame count threshold

    def start_threshold_calculation(self):
        """Start background thread to calculate ambient noise threshold."""
        thread = threading.Thread(target=self.run_calculate_threshold, daemon=True)
        thread.start()

    def run_calculate_threshold(self):
        """Continuously calculate and update ambient threshold."""
        while True:
            value = calculate_threshold()
            with self.lock:
                self.ambient_threshold = value
            self.calculation_done.set()
            time.sleep(1)

    def check_speech(self, stream):
        """
        Wait for speech based on ambient threshold.
        Abbruch nach 10 Sekunden ohne Spracheingabe.
        Gibt (speech_detected, keinerspricht) zurück.
        """
        threshold = self.ambient_threshold
        print("Listening for speech...")

        timeout_seconds = 30
        start_time = time.time()
        keinerspricht = False

        while True:
            if time.time() - start_time > timeout_seconds:
                print("🔇 Timeout: Keine Spracheingabe erkannt (10s)")
                keinerspricht = True
                return False, keinerspricht

            # calc ambient threshold 
            if self.calculation_done.is_set():
                with self.lock:
                    threshold = self.ambient_threshold
                    print(f"Using new ambient_threshold: {threshold}")
                self.calculation_done.clear()

            # read audio data 
            data, _ = stream.read(CHUNK)
            volume = np.abs(np.frombuffer(data, dtype=np.int16)).mean()
            print(f"Checking for speech... Volume: {volume}")

            # speech detected
            if volume > threshold + VOICE_DELTA:
                print("Speech detected, starting to record...")
                keinerspricht = False
                return True, keinerspricht

    def record_audio_frames(self, stream):
        """Record audio frames until extended silence is detected."""
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
        """Save recorded audio to BytesIO."""
        frames = np.concatenate(frames, axis=0)
        audio_stream = BytesIO()
        sf.write(audio_stream, frames, RATE, format="WAV")
        audio_stream.seek(0)
        audio_stream.name = "audio.wav"
        print("Recording saved to BytesIO stream successfully.")
        return audio_stream

    def record_audio(self):
        """Main function: Start, record, save, and return audio + flag."""
        self.start_threshold_calculation()
        stream = sd.InputStream(samplerate=RATE, dtype="int16", channels=1, blocksize=CHUNK)
        stream.start()

        speech_detected, keinerspricht = self.check_speech(stream)

        if not speech_detected:
            stream.stop()
            stream.close()
            return None, keinerspricht

        frames = self.record_audio_frames(stream)

        stream.stop()
        stream.close()

        audio_stream = self.save_recording(frames)
        return audio_stream, keinerspricht


if __name__ == "__main__":
    recorder = VoiceRecorder()
    audio_stream, keinerspricht = recorder.record_audio()
    if keinerspricht:
        print("❌ Niemand hat gesprochen – Timeout erkannt.")
    else:
        print("✅ Sprache wurde erkannt und aufgezeichnet.")
