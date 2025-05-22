import fitz  # PyMuPDF

def extract_text_blocks(file_path):
    with fitz.open(file_path) as doc:
        return "\n".join([page.get_text() for page in doc])
