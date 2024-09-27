import logging
import os
from collections import Counter
import fitz  # PyMuPDF for PDF text extraction
import nltk
import requests
import textract
from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template, request
from transformers import AutoTokenizer, pipeline
from werkzeug.utils import secure_filename

nltk.download('punkt')
from nltk.tokenize import sent_tokenize

# Initialize emotion analysis model
MODEL_NAME = 'j-hartmann/emotion-english-distilroberta-base'
emotion_analyzer = pipeline('sentiment-analysis', model=MODEL_NAME)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# Flask app setup
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'rtf', 'md', 'odt', 'html'}
logging.basicConfig(level=logging.DEBUG)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_file(file_path, file_ext):
    try:
        if file_ext == 'pdf':
            return extract_text_from_pdf(file_path)
        return textract.process(file_path).decode('utf-8')
    except Exception as e:
        logging.error(f"Text extraction failed: {e}")
        return ""


def extract_text_from_pdf(file_path):
    try:
        text = ""
        pdf_document = fitz.open(file_path)
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        pdf_document.close()
        return text
    except Exception as e:
        logging.error(f"PDF text extraction failed: {e}")
        return ""


def analyze_emotions(text):
    sentences = sent_tokenize(text)
    results = []
    for i, sentence in enumerate(sentences):
        result = emotion_analyzer(sentence)
        for r in result:
            r['position'] = i
        results.extend(result)
    return results


def aggregate_emotions(emotions):
    emotion_counter = Counter()
    scores = {emotion: [] for emotion in set(e['label'] for e in emotions)}

    for emotion_data in emotions:
        emotion_counter[emotion_data['label']] += 1
        scores[emotion_data['label']].append(emotion_data['score'])

    avg_scores = {emotion.lower(): (sum(scores[emotion]) / len(scores[emotion])) for emotion in scores}
    return emotion_counter, avg_scores


def extract_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        return ' '.join([p.get_text() for p in paragraphs])
    except Exception as e:
        logging.error(f"Error extracting text from URL: {e}")
        return ""


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        logging.error("No file part in the request")
        return jsonify({"error": "No file part"})

    file = request.files['file']
    if file.filename == '':
        logging.error("No file selected")
        return jsonify({"error": "No selected file"})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        try:
            file.save(file_path)
            text = extract_text_from_file(file_path, filename.rsplit('.', 1)[1].lower())
            emotions = analyze_emotions(text)
            emotion_counts, avg_scores = aggregate_emotions(emotions)
            os.remove(file_path)  # Cleanup after processing
            return jsonify({
                "emotion_counts": emotion_counts,
                "average_scores": avg_scores,
            })
        except Exception as e:
            logging.error(f"File processing error: {e}")
            return jsonify({"error": str(e)})
    else:
        logging.error("File type not allowed")
        return jsonify({"error": "File type not allowed"})


@app.route('/analyze_url', methods=['POST'])
def analyze_url():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "No URL provided"})

    try:
        text = extract_text_from_url(url)
        emotions = analyze_emotions(text)
        emotion_counts, avg_scores = aggregate_emotions(emotions)
        return jsonify({
            "emotion_counts": emotion_counts,
            "average_scores": avg_scores,
        })
    except Exception as e:
        logging.error(f"Error processing URL: {e}")
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
