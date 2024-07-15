from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import os
from dashboard import create_dash_app

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return redirect(url_for('dash_page', filename=filename))
    return redirect(request.url)


@app.route('/dashboard')
def dash_page():
    filename = request.args.get('filename')
    if filename:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        return redirect(f'/dash?filename={filename}')
    else:
        return redirect(url_for('index'))


# Create and register Dash application
dash_app = create_dash_app(app)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
