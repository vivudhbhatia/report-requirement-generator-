import fitz  # PyMuPDF
import re

def extract_text_blocks(file_path):
    text_blocks = []
    with fitz.open(file_path) as doc:
        for page in doc:
            blocks = page.get_text("blocks")
            for b in blocks:
                text = b[4].strip()
                if text:
                    text_blocks.append(text)
    return "\n".join(text_blocks)

def extract_sections(text):
    pattern = r"(Schedule\s+[A-Z]+\s*[\—\-–]?[^\n]*)"
    return re.split(pattern, text)[1:]  # Splits and returns in [header, content, header, content,...]
