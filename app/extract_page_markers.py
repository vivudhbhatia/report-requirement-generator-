import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
import argparse


def extract_from_text(pdf_path, max_pages=6):
    doc = fitz.open(pdf_path)
    toc_lines = []

    for page_num in range(min(max_pages, len(doc))):
        text = doc.load_page(page_num).get_text()
        for line in text.splitlines():
            if re.search(r'\.{3,}\s*\w+-?\d+$', line):  # Dotted lines ending with GEN-1, A-1 etc.
                toc_lines.append((page_num + 1, line.strip()))
    
    return toc_lines


def extract_from_ocr(pdf_path, max_pages=6):
    doc = fitz.open(pdf_path)
    toc_lines = []

    for page_num in range(min(max_pages, len(doc))):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        image = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(image)

        for line in text.splitlines():
            if re.search(r'\.{3,}\s*\w+-?\d+$', line):
                toc_lines.append((page_num + 1, line.strip()))
    
    return toc_lines


def extract_page_markers(pdf_path, max_pages=6):
    toc_lines = extract_from_text(pdf_path, max_pages)
    if not toc_lines:
        print("No page markers found via text extraction. Falling back to OCR...")
        toc_lines = extract_from_ocr(pdf_path, max_pages)
    return toc_lines


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract TOC-style page markers from PDF.")
    parser.add_argument("pdf_path", help="Path to the input PDF file.")
    parser.add_argument("--max_pages", type=int, default=6, help="Number of initial pages to scan.")
    args = parser.parse_args()

    results = extract_page_markers(args.pdf_path, args.max_pages)

    if results:
        print("\n🧾 Extracted Page Markers:")
        for page_num, line in results:
            print(f"[PDF Page {page_num}] {line}")
    else:
        print("❌ No page markers found in the provided PDF.")
