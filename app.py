from flask import Flask, request, render_template, send_from_directory
import os
import datetime

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Store file information: (filename, upload_time, client_ip)
uploaded_files_info = []

@app.route('/')
def index():
    return render_template('index.html', files=uploaded_files_info)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = file.filename
    client_ip = request.remote_addr  # Get the client's IP address
    upload_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Save the file to the uploads directory
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Store the file information (filename, upload time, client IP)
    uploaded_files_info.append((filename, upload_time, client_ip))

    return 'File uploaded successfully', 200

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
    app.run(debug=True)

