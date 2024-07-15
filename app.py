from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import os
from dashboard import create_dash_app
import logging

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Setup logging
logging.basicConfig(level=logging.DEBUG)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def index():
    return render_template('index.html', title='AnalytiCore')


@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    logging.debug("Entered upload_file route")
    if 'file' not in request.files:
        logging.debug("No file part in request")
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        logging.debug("No file selected")
        return redirect(request.url)
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        logging.debug(f"File saved to {file_path}")
        return redirect(url_for('dashboard', filepath=file_path))
    logging.debug("File is not a CSV")
    return redirect(request.url)


@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    filepath = request.args.get("filepath")
    logging.debug(f"Dashboard accessed with filepath: {filepath}")
    return redirect(f'/dash/?filepath={filepath}')


# Create Dash app
create_dash_app(app)

if __name__ == '__main__':
    app.run(debug=True)
