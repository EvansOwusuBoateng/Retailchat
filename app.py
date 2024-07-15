from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import os
from dashboard import create_dash_app

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def index():
    return render_template('index.html', title='AnalytiCore')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return redirect(url_for('dashboard', filepath=file_path))
    return redirect(request.url)


@app.route('/dashboard')
def dashboard():
    filepath = request.args.get("filepath")
    return redirect(f'/dash/?filepath={filepath}')


# Create Dash app
create_dash_app(app)

if __name__ == '__main__':
    app.run(debug=True)
