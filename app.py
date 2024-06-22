import logging
import os
from collections import Counter

import fitz  # PyMuPDF
import nltk
import requests
import textract
from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template, request
from transformers import AutoTokenizer, pipeline
from werkzeug.utils import secure_filename

nltk.download('punkt')
from nltk.tokenize import sent_tokenize

# Initialize the emotion analysis pipeline and tokenizer
model_name = 'j-hartmann/emotion-english-distilroberta-base'
emotion_analyzer = pipeline('sentiment-analysis', model=model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'rtf', 'md', 'odt', 'html'}

logging.basicConfig(level=logging.DEBUG)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_file(file_path, file_ext):
    if file_ext == 'pdf':
        text = extract_text_from_pdf(file_path)
    else:
        text = textract.process(file_path).decode('utf-8')
    return text


def extract_text_from_pdf(file_path):
    text = ""
    pdf_document = fitz.open(file_path)
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    pdf_document.close()
    return text


def analyze_emotions_with_positions(text):
    sentences = sent_tokenize(text)
    results = []
    for i, sentence in enumerate(sentences):
        result = emotion_analyzer(sentence)
        for r in result:
            r['position'] = i
        results.extend(result)
    return results


def aggregate_emotions(results):
    emotion_counter = Counter()
    for result in results:
        emotion_counter[result['label']] += 1
    average_scores = {}
    for emotion in emotion_counter.keys():
        emotion_scores = [result['score'] for result in results if result['label'] == emotion]
        average_scores[emotion.lower()] = sum(emotion_scores) / len(emotion_scores)
    return emotion_counter, average_scores


def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    text = ' '.join([para.get_text() for para in paragraphs])
    return text


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
            file_ext = filename.rsplit('.', 1)[1].lower()
            text = extract_text_from_file(file_path, file_ext)
            emotions = analyze_emotions_with_positions(text)
            emotion_counts, average_scores = aggregate_emotions(emotions)
            positions = {emotion: [] for emotion in emotion_counts.keys()}
            for e in emotions:
                positions[e['label'].lower()].append(e['position'])
            os.remove(file_path)
            return jsonify({
                "emotion_counts": emotion_counts,
                "average_scores": average_scores,
                "positions": positions
            })
        except Exception as e:
            logging.error(f"Error processing file: {e}")
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
        emotions = analyze_emotions_with_positions(text)
        emotion_counts, average_scores = aggregate_emotions(emotions)
        positions = {emotion: [] for emotion in emotion_counts.keys()}
        for e in emotions:
            positions[e['label'].lower()].append(e['position'])
        return jsonify({
            "emotion_counts": emotion_counts,
            "average_scores": average_scores,
            "positions": positions
        })
    except Exception as e:
        logging.error(f"Error processing URL: {e}")
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
