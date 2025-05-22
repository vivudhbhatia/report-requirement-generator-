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
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code != 200 or b'%PDF' not in response.content[:1024]:
        raise ValueError("❌ URL did not return a valid PDF file.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(response.content)
        tmp.flush()
        try:
            doc = fitz.open(tmp.name)
            return "\n".join([page.get_text() for page in doc])
        except Exception as e:
            raise ValueError(f"❌ Failed to open PDF file. Reason: {str(e)}")
