from flask import Flask, render_template, request, jsonify, url_for #Added url_for
import hashlib
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import PyPDF2
import docx
from werkzeug.exceptions import RequestEntityTooLarge #Import exception

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB limit #Upload a max of 4MB for comparison


# Download NLTK resources (do this once, if needed)
try:
    stopwords.words('english')
except LookupError:
    nltk.download('stopwords')
try:
    PorterStemmer()
except LookupError:
    nltk.download('punkt')

def preprocess_text(text):
    """Preprocesses the text for plagiarism detection."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]
    stemmer = PorterStemmer()
    words = [stemmer.stem(word) for word in words]
    return " ".join(words)

def rolling_hash_sha256(text, window_size):
    """Calculates rolling hashes using SHA256."""
    hashes = []
    for i in range(len(text) - window_size + 1):
        window_text = text[i:i + window_size].encode('utf-8')
        current_hash = hashlib.sha256(window_text).hexdigest()
        hashes.append(current_hash)
    return hashes

def compare_documents_rolling_hash(doc1, doc2, window_size=20, threshold=0.8):
    """Compares two documents using rolling hashes."""
    hashes1 = rolling_hash_sha256(doc1, window_size)
    hashes2 = rolling_hash_sha256(doc2, window_size)

    matches = 0
    min_len = min(len(hashes1), len(hashes2))

    for i in range(min_len):
        if hashes1[i] == hashes2[i]:
            matches += 1

    similarity = 0
    if min_len > 0:
        similarity = matches / min_len

    return similarity >= threshold, similarity

def read_file(file):
    """Reads the content of an uploaded file, handling different file types."""
    if not file:
        return ""

    filename = file.filename

    if filename.lower().endswith('.txt'):
        return file.read().decode('utf-8')
    elif filename.lower().endswith('.pdf'):
        try:
            pdf_reader = PyPDF2.PdfReader(file.read())
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            return f"Error reading PDF: {e}"
    elif filename.lower().endswith('.docx'):
        try:
            doc = docx.Document(file.read())
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            return f"Error reading DOCX: {e}"
    else:
        return "Unsupported file type"
    

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':
            file1 = request.files['file1']
            file2 = request.files['file2']
            window_size = int(request.form['window_size'])
            threshold = float(request.form['threshold'])

            doc1_content = read_file(file1)
            doc2_content = read_file(file2)

            doc1_processed = preprocess_text(doc1_content)
            doc2_processed = preprocess_text(doc2_content)

            are_similar, similarity_score = compare_documents_rolling_hash(doc1_processed, doc2_processed, window_size, threshold)

            result = {
                'similarity_score': similarity_score,
                'are_similar': are_similar
            }

            return jsonify(result)

        return render_template('index.html')

    except RequestEntityTooLarge:
        return jsonify({'error': 'File size exceeded 4MB limit'}), 413

if __name__ == '__main__':
    app.run(debug=True)