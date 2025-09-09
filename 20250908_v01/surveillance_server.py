from flask import Flask, request, render_template, send_file
import os
from datetime import datetime
import glob

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_file_size(bytes_size):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

@app.route('/')
def index():
    """Main page showing uploaded files"""
    files = []
    for file_path in glob.glob(os.path.join(UPLOAD_FOLDER, '*')):
        if os.path.isfile(file_path):
            filename = os.path.basename(file_path)
            file_size = get_file_size(os.path.getsize(file_path))
            upload_time = datetime.fromtimestamp(os.path.getctime(file_path))
            file_type = filename.split('.')[-1].upper() if '.' in filename else 'UNKNOWN'
            
            files.append({
                'name': filename,
                'size': file_size,
                'type': file_type,
                'upload_time': upload_time.strftime('%Y-%m-%d %H:%M:%S'),
                'path': file_path
            })
    
    # Sort by upload time (newest first)
    files.sort(key=lambda x: x['upload_time'], reverse=True)
    
    return render_template('index.html', files=files, current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file uploads from client"""
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    
    if file:
        # Create unique filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_name = file.filename
        filename = f"{timestamp}_{original_name}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save file
        file.save(filepath)
        
        print(f"Uploaded: {filename} ({get_file_size(os.path.getsize(filepath))})")
        return f'File uploaded successfully: {filename}', 200

@app.route('/download/<filename>')
def download_file(filename):
    """Download a file"""
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return "File not found", 404

@app.route('/delete/<filename>')
def delete_file(filename):
    """Delete a file"""
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return f"File {filename} deleted successfully", 200
    return "File not found", 404

@app.route('/view')
def view_files():
    """Simple file list view"""
    files = []
    for file_path in glob.glob(os.path.join(UPLOAD_FOLDER, '*')):
        if os.path.isfile(file_path):
            files.append({
                'name': os.path.basename(file_path),
                'size': get_file_size(os.path.getsize(file_path)),
                'time': datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    files.sort(key=lambda x: x['time'], reverse=True)
    
    html = "<h1>Uploaded Files</h1>"
    html += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
    html += "<tr><th>Filename</th><th>Size</th><th>Upload Time</th><th>Action</th></tr>"
    
    for file in files:
        html += f"""
        <tr>
            <td>{file['name']}</td>
            <td>{file['size']}</td>
            <td>{file['time']}</td>
            <td><a href='/download/{file['name']}'>Download</a></td>
        </tr>
        """
    
    html += "</table>"
    html += f"<p>Total files: {len(files)}</p>"
    html += "<p><a href='/'>Back to main page</a></p>"
    
    return html

if __name__ == '__main__':
    print("Starting Flask server on http://127.0.0.1:5000")
    print("Upload folder:", UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5000, debug=True)