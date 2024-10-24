from app import app
from flask import request, render_template, url_for
import os

from werkzeug.utils import secure_filename

import numpy as np
from PIL import Image
import random
import string
import pytesseract
from ml import extract_text

app.config['INITIAL_FILE_UPLOADS'] = 'app/static/uploads'

@app.route('/', methods=['GET', 'POST'])
def index():
    full_filename = url_for('static', filename='images')
    if request.method == 'POST':
        image_upload = request.files['image_upload']
        # Save the file
        filename = secure_filename(image_upload.filename)
        filepath = os.path.join(app.config['INITIAL_FILE_UPLOADS'], filename)
        image_upload.save(filepath)
        
        extracted_text = extract_text(filepath)
        img_url = url_for('static', filename=f'uploads/{filename}')
        return render_template('index.html', img_url=img_url, full_filename=full_filename, extracted_text=extracted_text)
    else:
        return render_template('index.html', full_filename=full_filename)
    
if __name__ == '__main__':
    app.run(debug=True)