from flask import Flask, request, send_from_directory, render_template_string
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload():
    image = request.files.get('image')
    if image:
        filename = datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, 'wb') as f:
            f.write(image.read())
        return 'OK', 200
    return 'No image', 400

@app.route('/static/<path:filename>')
def serve_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/')
def index():
    files = os.listdir(UPLOAD_FOLDER)
    images = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Galerie Imagini</title>
    </head>
    <body>
        <h1>Imagini încărcate</h1>
        {% for image in images %}
            <div style="margin-bottom: 10px;">
                <img src="{{ url_for('serve_image', filename=image) }}" width="300"><br>
                <small>{{ image }}</small>
            </div>
        {% endfor %}
    </body>
    </html>
    '''
    return render_template_string(html, images=images)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
