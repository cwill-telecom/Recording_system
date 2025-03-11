import pyautogui
import cv2
import numpy as np
import datetime
import time
import requests

DURATION = 30  # Screen recording duration in seconds
FLASK_SERVER_URL = "http://127.0.0.1:5000/uploads"
OUTPUT_FILE = f"screenrecord_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.avi"

def record_screen():
    screen_size = pyautogui.size()
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(OUTPUT_FILE, fourcc, 10.0, screen_size)

    print(f"🔹 Screen recording started for {DURATION} seconds.")
    start_time = time.time()

    while time.time() - start_time < DURATION:
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out.write(frame)

    out.release()
    print(f"🔹 Screen recording saved: {OUTPUT_FILE}")
    upload_to_server()

def upload_to_server():
    with open(OUTPUT_FILE, "rb") as f:
        response = requests.post(FLASK_SERVER_URL, files={"file": f})
    print(f"📤 Uploaded {OUTPUT_FILE}: {response.text}")

if __name__ == "__main__":
    record_screen()
