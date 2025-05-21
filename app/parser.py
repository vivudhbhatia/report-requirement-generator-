import pdfplumber
import requests
import tempfile

def parse_pdf_from_file(file):
    with pdfplumber.open(file) as pdf:
        return "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])

def parse_pdf_from_url(url):
    response = requests.get(url)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(response.content)
        tmp.flush()
        return parse_pdf_from_file(tmp.name)
