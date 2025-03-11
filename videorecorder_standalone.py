import cv2
import datetime
import time
import requests

DURATION = 20  # Video recording duration in seconds
FLASK_SERVER_URL = "http://127.0.0.1:5000/uploads"
OUTPUT_FILE = f"webcam_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.avi"

def record_video():
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(OUTPUT_FILE, fourcc, 20.0, (640, 480))

    print(f"🔹 Video recording started for {DURATION} seconds.")
    start_time = time.time()

    while time.time() - start_time < DURATION:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        cv2.imshow("Video Recording", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"🔹 Video recording saved: {OUTPUT_FILE}")
    upload_to_server()

def upload_to_server():
    with open(OUTPUT_FILE, "rb") as f:
        response = requests.post(FLASK_SERVER_URL, files={"file": f})
    print(f"📤 Uploaded {OUTPUT_FILE}: {response.text}")

if __name__ == "__main__":
    record_video()
