import fitz  # PyMuPDF
import tempfile
import requests

def parse_pdf_from_file(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.read())
        tmp.flush()
        doc = fitz.open(tmp.name)
        return "\n".join([page.get_text() for page in doc])

def parse_pdf_from_url(url):
    response = requests.get(url)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(response.content)
        tmp.flush()
        doc = fitz.open(tmp.name)
        return "\n".join([page.get_text() for page in doc])
