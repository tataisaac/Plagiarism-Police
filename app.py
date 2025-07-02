'''Plagiarism Police'''
#-- Ver 1.0
#-- A Plagiarism Detection Application
#-- built on the streamlit library
#-- Developer: TATA I. FOMBANG
#-- tifombang@gmail.com

import streamlit as st
import fitz  # PyMuPDF for PDF handling //pip install PyMuPDF
from docx import Document  # python-docx for DOCX handling
import os
import tempfile
import re
import hashlib
from nltk.corpus import stopwords  # For stop words removal
from nltk.stem import PorterStemmer  # For stemming
import pandas as pd  # Import pandas
import nltk

nltk.download('stopwords')


def save_uploaded_file(uploaded_file):
    """-- Saves the uploaded file to a temporary file and returns the file path."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
        temp_file.write(uploaded_file.getvalue())
        return temp_file.name

def extract_text_from_pdf(file_path):
    """-- Extracts text from a PDF file."""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(file_path):
    """-- Extracts text from a DOCX file."""
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {e}")
        return ""

def extract_text_from_txt(file_path):
    """-- Extracts text from a TXT file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        st.error(f"Error extracting text from TXT: {e}")
        return ""

def extract_text(file_path, file_type):
    """-- Extracts text from a file based on its type."""
    if file_type == "pdf":
        return extract_text_from_pdf(file_path)
    elif file_type == "docx":
        return extract_text_from_docx(file_path)
    elif file_type == "txt":
        return extract_text_from_txt(file_path)
    else:
        st.error(f"Unsupported file type: {file_type}")
        return ""

def preprocess_text(text):
    """-- Preprocesses the text for plagiarism detection."""
    text = text.lower()  # Normalization: Convert to lowercase
    text = re.sub(r'[^\w\s]', '', text)  #Sanitization: Remove punctuation
    words = text.split()  #Tokenization: Splitting the text body into words
    stop_words = set(stopwords.words('english'))  # Load English stop words from the re library
    words = [word for word in words if word not in stop_words]  # Remove stop words
    stemmer = PorterStemmer()  # Initialize stemmer
    words = [stemmer.stem(word) for word in words]  # Stem words
    return " ".join(words)  # Join words back into a string

def rolling_hash_sha256(text, window_size):
    """-- Calculates rolling hashes using SHA256."""
    hashes = []
    for i in range(len(text) - window_size + 1):
        window_text = text[i:i + window_size].encode('utf-8')  # Encode window text
        current_hash = hashlib.sha256(window_text).hexdigest()  # Calculate SHA256 hash
        hashes.append(current_hash)
    return hashes

def compare_documents_rolling_hash(doc1, doc2, window_size=20, threshold=0.8):
    """-- Compares two documents using rolling hashes."""
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

#-- st.title("Plagiarism Police 1.0")
st.markdown("<h1 style='text-align: center;'>Plagiarism Police 1.0</h1>", unsafe_allow_html=True)


tab1, tab2, tab3 = st.tabs(["Compare Two Files", "Compare One to Many", "Online Sources"])

with tab1:
    st.header("Compare Two Files")
    uploaded_file1 = st.file_uploader("Upload File 1")
    uploaded_file2 = st.file_uploader("Upload File 2")

    if st.button("Compare"):
        if uploaded_file1 and uploaded_file2:
            #-- st.write("Procsssing...")

            file_extension1 = os.path.splitext(uploaded_file1.name)[1].lower()[1:]
            file_extension2 = os.path.splitext(uploaded_file2.name)[1].lower()[1:]

            temp_file1_path = save_uploaded_file(uploaded_file1)
            temp_file2_path = save_uploaded_file(uploaded_file2)

            text1 = extract_text(temp_file1_path, file_extension1)
            text2 = extract_text(temp_file2_path, file_extension2)

            os.remove(temp_file1_path)
            os.remove(temp_file2_path)

            if text1 and text2 and text1 != "" and text2 != "":
                processed_text1 = preprocess_text(text1)
                processed_text2 = preprocess_text(text2)
                progress_bar = st.progress(0) #initialize progress bar
                is_plagiarized, similarity = compare_documents_rolling_hash(processed_text1, processed_text2)
                progress_bar.progress(1.0) #progress bar to 100%

                st.write(f"Similarity: {similarity * 100:.2f}%")
                if is_plagiarized:
                    st.write("Plagiarism detected.")
                else:
                    st.write("No significant plagiarism detected.")
            else:
                st.write("There was an issue with one of the files")
        else:
            st.write("Please upload both files.")

with tab2:
    st.header("Compare one file to many")
    base_file = st.file_uploader("Upload Base File (.txt | .pdf | .docx)")
    uploaded_files = st.file_uploader("Upload Multiple Files", accept_multiple_files=True)

    if st.button("Scan"):  # Added Scan button
        if base_file and uploaded_files:
            base_file_path = save_uploaded_file(base_file)
            base_file_extension = os.path.splitext(base_file.name)[1].lower()[1:]
            base_text = extract_text(base_file_path, base_file_extension)
            os.remove(base_file_path)

            if base_text:
                results = []
                total_files = len(uploaded_files)
                progress_bar = st.progress(0)  # Initialize the progress bar
                
                for i, uploaded_file in enumerate(uploaded_files):
                    file_path = save_uploaded_file(uploaded_file)
                    file_extension = os.path.splitext(uploaded_file.name)[1].lower()[1:]
                    file_text = extract_text(file_path, file_extension)
                    os.remove(file_path)

                    if file_text:
                        processed_base_text = preprocess_text(base_text)
                        processed_file_text = preprocess_text(file_text)
                        is_plagiarized, similarity = compare_documents_rolling_hash(processed_base_text, processed_file_text)
                        results.append([uploaded_file.name, f"{similarity * 100:.2f}%", "Plagiarism detected" if is_plagiarized else "No plagiarism detected"])

                    progress_bar.progress((i + 1) / total_files)  # Update the progress bar


                if results:
                    # Create a Pandas DataFrame with column headers
                    data = []
                    for i, result in enumerate(results):
                        data.append([i + 1] + result)
                    df = pd.DataFrame(data, columns=["No.", "Filename", "Similarity Rate", "Verdict"])
                    st.table(df.set_index('No.'))
                else:
                    st.write("No valid files uploaded.")
            else:
                st.write("Error processing the base file.")
        elif base_file:
            st.write("Please upload multiple files.")
        elif uploaded_files:
            st.write("Please upload a base file.")
        else:
            st.write("Please upload a base file and multiple files.")


#-- Checking online sources
with tab3:
    st.write("Module under development")
    st.file_uploader("Upload a file")
    st.button("Scan Online")