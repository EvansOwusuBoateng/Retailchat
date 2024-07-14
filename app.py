from flask import Flask, render_template, request, redirect, flash, url_for
from werkzeug.utils import secure_filename
import os
import secrets
from dashboard import create_dash_app

# Set the upload folder relative to the application root directory
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = secrets.token_hex(16)  # Set a unique and secret key


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html', title='AnalytiCore')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        file.save(file_path)
        flash('File successfully uploaded')

        # Redirect to Dash application's URL with the uploaded file path as a query parameter
        return redirect(url_for('dash_page', file=file_path))

    flash('Allowed file types are csv')
    return redirect(request.url)


@app.route('/dash/')
def dash_page():
    file_path = request.args.get('file')
    if not file_path or not os.path.exists(file_path):
        flash('File not found')
        return redirect(url_for('index'))

    # Pass the file path to the Dash app or handle accordingly
    return redirect(f'/dash/?file={file_path}')


if __name__ == '__main__':
    dash_app = create_dash_app(app)
    app.run(debug=True)  # Run the Flask application in debug mode for troubleshooting
