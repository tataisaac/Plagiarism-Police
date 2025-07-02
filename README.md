# Plagiarism Police 1.0

A Plagiarism Detection Application built on the Streamlit library.

## About the Project
Plagiarism Police 1.0 is a user-friendly tool for detecting plagiarism in PDF, DOCX, and TXT files. It uses text preprocessing, rolling hash, and similarity comparison to identify potential plagiarism between documents. The app is built with Streamlit for an interactive web interface.

**Developer:** TATA I. FOMBANG  
**Email:** tifombang@gmail.com

## Features
- Compare two files for plagiarism
- Compare one file against many
- Support for PDF, DOCX, and TXT files
- Uses NLTK for text preprocessing
- Rolling hash and similarity detection
- (Upcoming) Compare a file to online sources and datasets *(feature under development)*

## Getting Started

### Prerequisites
- Python 3.8+

### Setup Instructions
1. Clone the repository:
   ```
   git clone <your-repo-url>
   cd Plagiarism-Police 1.0
   ```
2. Create and activate a virtual environment (recommended):
   ```
   python -m venv .venv
   .\.venv\Scripts\Activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Download NLTK stopwords (first run only):
   The app will automatically download stopwords on first run, or you can run:
   ```python
   import nltk
   nltk.download('stopwords')
   ```
5. Start the app:
   ```
   streamlit run main.py
   ```

## Credits
Developed by TATA I. FOMBANG

## License
This project is for educational and demonstration purposes.


## Acknowledgements

I developed this application as a mini project for the course **Advanced Data Structures and Algorithms** during my studies in the **MTech in Networks and Information Security** program at **CHITECHMA University, Buea, Cameroon**.
