# Emotion Analysis Application

## Overview

This project is a web-based application designed to analyze emotions from uploaded text files or URLs. The application uses a deep learning model for sentiment analysis to detect emotions such as joy, surprise, sadness, disgust, anger, fear, and neutral from the text. It then visualizes these emotions using various charts. The backend is built using Flask, and the frontend uses HTML, CSS, and JavaScript.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Usage](#usage)
5. [File Structure](#file-structure)
6. [Detailed Component Explanation](#detailed-component-explanation)
7. [Dependencies](#dependencies)
8. [Acknowledgements](#acknowledgements)

## Getting Started

These instructions will help you set up the project on your local machine for development and testing purposes.

### Prerequisites

Ensure you have the following software installed on your system:
- Python 3.6+
- pip (Python package installer)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/emotion-analysis-app.git
   cd emotion-analysis-app
   ```

2. **Install required Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download NLTK data:**
   ```python
   import nltk
   nltk.download('punkt')
   ```

4. **Run the Flask application:**
   ```bash
   python app.py
   ```

The application should now be running on `http://127.0.0.1:5000/`.

## Usage

### Uploading a File

1. Open the application in your web browser.
2. Click on the "Drag file or click to select" area to upload a file.
3. Select a text file (e.g., .txt, .pdf, .docx).
4. The application will analyze the file and display the detected emotions in various charts.

### Analyzing a URL

1. Open the application in your web browser.
2. Enter a URL in the "Paste the URL for analysis" input box.
3. Click on the "Parse URL" button.
4. The application will fetch the text from the URL, analyze it, and display the detected emotions in various charts.

## File Structure

The project directory contains the following files:

- `app.py`: The main Flask application script.
- `requirements.txt`: List of Python dependencies.
- `templates/index.html`: The main HTML template for the application.
- `static/styles.css`: The CSS file for styling the frontend.
- `static/script.js`: The JavaScript file for frontend logic and interactions.

## Detailed Component Explanation

### 1. Backend (`app.py`)

- **Flask Setup:**
  Initializes the Flask application, sets up routes, and configures the upload folder.
  
- **Emotion Analysis Pipeline:**
  Uses the `transformers` library to load a pre-trained emotion analysis model and tokenizer.

- **Text Extraction:**
  Functions to extract text from different file types (e.g., PDF, DOCX) and URLs using libraries like `textract`, `PyMuPDF`, and `BeautifulSoup`.

- **Emotion Analysis:**
  Functions to analyze emotions in the text and aggregate the results. Sentences are tokenized, analyzed, and emotions are counted and averaged.

- **Routes:**
  - `/`: Serves the main HTML page.
  - `/upload`: Handles file uploads and returns emotion analysis results.
  - `/analyze_url`: Handles URL submissions and returns emotion analysis results.

### 2. Frontend (`index.html`, `styles.css`, `script.js`)

- **HTML (`index.html`):**
  - Defines the structure of the web page including input fields for file upload and URL input.
  - Includes placeholders for charts that will display the emotion analysis results.

- **CSS (`styles.css`):**
  - Styles the web page for better user experience and visual appeal.
  - Includes responsive design to ensure the page looks good on various screen sizes.

- **JavaScript (`script.js`):**
  - Handles user interactions such as file uploads and URL submissions.
  - Communicates with the backend to send files/URLs and receive analysis results.
  - Uses Chart.js to create and update charts based on the received data.

## Dependencies

The project relies on several Python packages and JavaScript libraries:

### Python Packages

- `flask`: Web framework for building the backend.
- `requests`: For making HTTP requests to fetch data from URLs.
- `beautifulsoup4`: For parsing HTML and extracting text from web pages.
- `transformers`: For loading and using the pre-trained emotion analysis model.
- `torch`: PyTorch, a deep learning framework used by the transformers library.
- `nltk`: For tokenizing text into sentences.
- `PyMuPDF`: For extracting text from PDF files.
- `textract`: For extracting text from various file formats.

### JavaScript Libraries

- `Chart.js`: For creating and displaying charts on the frontend.

## Acknowledgements

This project uses the `j-hartmann/emotion-english-distilroberta-base` model from the Hugging Face model hub for emotion detection. Special thanks to the creators and maintainers of the open-source libraries and tools used in this project.

