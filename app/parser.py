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
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, allow_redirects=True)

    content_type = response.headers.get("Content-Type", "")
    if "application/pdf" not in content_type and b"%PDF" not in response.content[:1024]:
        raise ValueError(f"❌ URL did not return a PDF (Content-Type: {content_type})")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(response.content)
        tmp.flush()
        doc = fitz.open(tmp.name)
        return "\n".join([page.get_text() for page in doc])
