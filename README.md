# Recording_system
Overview This project consists of two main components:  Client (client.py) – Captures keystrokes, records screen, webcam, and audio, and uploads the recorded files to a Flask server at regular intervals. Flask Server (app.py) – Hosts an upload endpoint to receive and store files sent by the client, allowing downloads of recorded content.<br>


⚠ Disclaimer: This is proof-of-concept code and is likely to be buggy and unstable. It is strictly for educational purposes only and should not be used for unauthorized monitoring or data collection.

🛠 Features<br>

<b>Client (client.py):</b><br>
Records keystrokes, screen activity, webcam footage, and audio.<br>
Automatically uploads recorded files to a Flask server every 178 seconds.<br>
Deletes old recordings to manage storage.<br>
Runs in the background and auto-restarts after each recording session.<br>

<b>Server (app.py):</b><br>
Hosts an upload endpoint to receive files.<br>
Stores uploaded recordings in the /uploads directory.<br>
Provides a web interface to view uploaded files.<br>
Allows downloading of stored files.<br>

# Installation Requirements
Install necessary dependencies using:

```bash
pip install keyboard pyautogui opencv-python requests sounddevice numpy wave

```
or

```bash
pip install -r requirments.txt

```

# Usage Instructions

Server (app.py)<br>
Run app.py on the server machine.<br>
```bash
python app.py

```
Ensure the /uploads directory exists and is writable.<br>
Visit http://127.0.0.1:5000/ in a browser to view uploaded files.<br>

Client (client.py)<br>
Modify FLASK_SERVER_URL in client.py to point to your server’s IP address if running remotely.<br>
Run client.py on the machine you want to record from.<br>
```bash
python client.py

```
The client will automatically record and upload data every 178 seconds.<br>


# Setting Up the templates Folder and index.html File<br>
The Flask server (app.py) renders an HTML page to display uploaded files. Flask expects HTML templates to be stored inside a templates/ folder.<br>
<b>How the index.html File Works</b><br>
Displays a list of uploaded files with their names, upload timestamps, and the IP address of the client that uploaded them.<br>
Provides a "Download" link for each file, allowing users to download files directly from the server.<br>
Uses Flask's url_for('download_file', filename=file[0]) to dynamically generate download links.<br>
# How the Programs Work<br>
Client (client.py)<br>
Keylogger: Captures keystrokes and writes them to a text file.<br>
Screen Recorder: Takes continuous screenshots and saves them as a video file.<br>
Webcam Recorder: Captures footage from the webcam and saves it as a video file.<br>
Audio Recorder: Records microphone input and saves it as a .wav file.<br>
File Uploader: Sends recorded files to the Flask server every 178 seconds.<br>
File Cleaner: Deletes old files to free up storage space.<br>
Auto-Restart Mechanism: Restarts the client process after every recording session to ensure continued operation.<br>

Server (app.py)<br>
Receives uploaded files from the client via an HTTP POST request.<br>
Stores files in the /uploads directory.<br>
Displays uploaded files in a web interface.<br>
Allows file downloads via a /download/<filename> endpoint.<br>

# Standalone Applications with Automatic Upload to Flask Server
Each script now automatically uploads the recorded files (keylogs, screen recordings, video, and audio)
to a Flask server after completion.
```bash
python keylogger.py       # Runs keylogger for 60 seconds
python screenrecorder.py  # Captures screen for 30 seconds
python videorecorder.py   # Records webcam for 20 seconds
python audiorecorder.py   # Records audio for 15 seconds

```
Features of This System<br>
✅ Standalone apps for keylogging, screen, video, and audio recording<br>
✅ Each app automatically stops after a set duration<br>
✅ Files are automatically uploaded to the Flask server<br>
✅ Ensures smooth execution and data transfer<br>

# ⚠ Disclaimer & Warning<br>
This project is for educational and proof-of-concept purposes only.<br>

This software is experimental and may be buggy.<br>
Unauthorized use of this software for monitoring or surveillance is illegal and could lead to severe consequences.<br>
The developers do not take responsibility for any misuse of this code.<br>

# 📜 License<br>
This project is licensed under MIT License. See LICENSE for details.
