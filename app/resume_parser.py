import fitz
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def extract_text_from_pdf(file_bytes):
    """Extract text from PDF bytes directly."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text
