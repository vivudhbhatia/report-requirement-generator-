import fitz
import tempfile
import requests

def parse_pdf_from_file(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.read())
        tmp.flush()
        doc = fitz.open(tmp.name)
        return "\n".join([page.get_text() for page in doc])

def parse_pdf_from_url(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if "application/pdf" not in response.headers.get("Content-Type", ""):
        raise ValueError("Not a valid PDF.")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(response.content)
        tmp.flush()
        doc = fitz.open(tmp.name)
        return "\n".join([page.get_text() for page in doc])
