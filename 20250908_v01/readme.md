# Surveillance System

A comprehensive surveillance system that captures screen activity, webcam footage, audio recordings, keystrokes, and screenshots, then automatically uploads them to a central server.

## 🚀 Features

### Client Capabilities
- **Screen Recording**: Captures desktop activity
- **Webcam Recording**: Records video from webcam
- **Audio Recording**: Captures microphone audio
- **Keylogging**: Logs all keystrokes with timestamps
- **Screenshots**: Takes periodic screenshots
- **System Information**: Collects detailed system specs
- **Auto Upload**: Automatically sends files to server
- **File Cleanup**: Removes old files to save space

### Server Features
- **File Upload Handling**: REST API for receiving files
- **Web Interface**: Beautiful dashboard to view uploaded files
- **File Management**: Download and delete files through web UI
- **Real-time Updates**: Auto-refreshing file list
- **Search Functionality**: Filter files by name
- **Statistics**: Display server metrics and file counts

## 📦 Installation

### Prerequisites
- Python 3.7+
- Webcam (optional, for video recording)
- Microphone (optional, for audio recording)

### Quick Setup
1. **Clone or download the project files**
2. **Install dependencies**:
   ```bash
   pip install flask requests opencv-python pyautogui keyboard pyaudio numpy psutil
   ```

3. **Create project structure**:
   ```
   surveillance_system/
   ├── server.py
   ├── surveillance_client.py
   ├── templates/
   │   └── index.html
   └── uploads/ (auto-created)
   ```

## 🛠️ Usage

### Starting the Server
```bash
python server.py
```
Server will start on: `http://127.0.0.1:5000`

### Starting the Client
```bash
python surveillance_client.py
```

### Accessing the Web Interface
Open your browser and navigate to: `http://127.0.0.1:5000`

## ⚙️ Configuration

### Client Configuration (in surveillance_client.py)
```python
CONFIG = {
    "flask_server_url": "http://127.0.0.1:5000/upload",
    "upload_interval": 60,  # seconds between upload cycles
    "max_file_age": 300,    # seconds before files are deleted
    "screen_duration": 30,  # seconds to record screen
    "video_duration": 30,   # seconds to record webcam
    "audio_duration": 30,   # seconds to record audio
    "keylog_interval": 30,  # seconds between keylog saves
    "max_retries": 3,       # upload retry attempts
    "upload_timeout": 10,   # seconds for upload timeout
    "data_dir": "client_data"  # local storage directory
}
```

### Server Configuration (in server.py)
- **Port**: Change `port=5000` to use a different port
- **Upload Folder**: Modify `UPLOAD_FOLDER = 'uploads'` to change storage location

## 📁 File Types Captured

- **Screen Recordings**: `screen_*.avi`
- **Webcam Videos**: `webcam_*.avi`
- **Audio Recordings**: `audio_*.wav`
- **Keylogs**: `keylog_*.txt` (includes system information)
- **Screenshots**: `screenshot_*.png`

## 🌐 Web Interface Features

- **File Listing**: View all uploaded files in a sortable table
- **Search**: Filter files by filename
- **File Type Indicators**: Color-coded file type badges
- **Download**: One-click file downloads
- **Delete**: Remove files from server
- **Auto-refresh**: Page updates every 30 seconds
- **Statistics**: Total file count and server status

## 🔧 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   pip install missing-module-name
   ```

2. **Webcam not working**
   - Ensure webcam is connected and accessible
   - Check privacy settings for camera access

3. **Audio not recording**
   - Check microphone permissions
   - Verify microphone is not muted

4. **Upload failures**
   - Verify server is running
   - Check network connectivity
   - Verify server URL in client configuration

### Port Conflicts
If port 5000 is busy, change the server port:
```python
# In server.py, change:
app.run(host='0.0.0.0', port=5000, debug=True)
# To:
app.run(host='0.0.0.0', port=8080, debug=True)  # or any free port
```

## ⚠️ Legal Disclaimer

**This software is intended for educational and ethical purposes only.** 

- Use only on systems you own or have explicit permission to monitor
- Comply with all local, state, and federal laws
- Inform users when they are being monitored (where required by law)
- Do not use for illegal activities or unauthorized surveillance

The developers are not responsible for misuse of this software.

## 🛡️ Privacy Considerations

- Files are stored locally on the client before upload
- All data is transmitted to the specified server
- No external data sharing beyond your configured server
- Files are automatically cleaned up after expiration

## 🔄 Automation

### Running as Service (Linux)
```bash
# Create a service file
sudo nano /etc/systemd/system/surveillance.service

# Add:
[Unit]
Description=Surveillance Client
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/surveillance_system
ExecStart=/usr/bin/python3 /path/to/surveillance_system/surveillance_client.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable surveillance.service
sudo systemctl start surveillance.service
```

### Scheduled Tasks (Windows)
Use Task Scheduler to run the client at startup or on a schedule.

## 📊 Monitoring

Check client status by looking for:
- Success messages in console output
- Files appearing in the web interface
- Network activity to the server

## 🗑️ Cleanup

- Client automatically deletes files older than `max_file_age`
- Server files must be manually deleted through web interface
- To completely remove: delete the `client_data` and `uploads` folders

## 🤝 Support

For issues and questions:
1. Check the troubleshooting section above
2. Verify all dependencies are installed
3. Ensure proper file permissions
4. Check firewall settings for network connectivity

## 📄 License

This project is for educational purposes. Use responsibly and ethically.

---

**Remember**: Always obtain proper authorization before monitoring any system. Respect privacy laws and regulations.
