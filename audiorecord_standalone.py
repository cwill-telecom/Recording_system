import sounddevice as sd
import numpy as np
import wave
import datetime
import requests

DURATION = 15  # Audio recording duration in seconds
FLASK_SERVER_URL = "http://127.0.0.1:5000/uploads"
SAMPLE_RATE = 44100
OUTPUT_FILE = f"audio_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.wav"

def record_audio():
    print(f"🔹 Recording audio for {DURATION} seconds...")
    audio_data = sd.rec(int(SAMPLE_RATE * DURATION), samplerate=SAMPLE_RATE, channels=2, dtype=np.int16)
    sd.wait()

    with wave.open(OUTPUT_FILE, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_data.tobytes())

    print(f"🔹 Audio recording saved: {OUTPUT_FILE}")
    upload_to_server()

def upload_to_server():
    with open(OUTPUT_FILE, "rb") as f:
        response = requests.post(FLASK_SERVER_URL, files={"file": f})
    print(f"📤 Uploaded {OUTPUT_FILE}: {response.text}")

if __name__ == "__main__":
    record_audio()
