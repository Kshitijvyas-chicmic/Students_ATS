import fitz
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def extract_text_from_pdf(path):
    full_path = os.path.join(BASE_DIR, path)
    doc = fitz.open(full_path)

    text = ""
    for page in doc:
        text += page.get_text()

    return text
