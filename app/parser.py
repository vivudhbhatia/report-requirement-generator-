import fitz
import tempfile
import requests

def parse_pdf_from_file(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.read())
        tmp.flush()
        doc = fitz.open(tmp.name)
        text = "\n".join([page.get_text() for page in doc])
        title_text = doc[0].get_text()
        return text, title_text
