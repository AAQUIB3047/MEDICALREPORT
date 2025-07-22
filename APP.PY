from flask import Flask, render_template, request, jsonify
import pytesseract
from PIL import Image
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')  # Make sure index.html is in a "templates" folder

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # OCR Extraction
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img)
        os.remove(filepath)  # Optional: cleanup

        # Basic keyword logic
        text_lower = text.lower()
        if "fever" in text_lower and "cough" in text_lower:
            prediction = "Likely Flu or COVID-like Symptoms"
        elif "fever" in text_lower:
            prediction = "Possible Fever or Infection"
        elif "cough" in text_lower:
            prediction = "Viral Cold"
        else:
            prediction = "Could not detect disease"

        # Return the result
        return jsonify({
            "text": text.strip(),
            "prediction": prediction
        })

    except Exception as e:
        return jsonify({'error': f"Failed to analyze image: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
