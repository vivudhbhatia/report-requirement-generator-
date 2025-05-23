import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
import argparse

def extract_from_text(pdf_path, max_pages=15):
    doc = fitz.open(pdf_path)
    toc_lines = []

    for page_num in range(min(max_pages, len(doc))):
        text = doc.load_page(page_num).get_text()

        for line in text.splitlines():
            if re.search(r'\.{3,}\s*\w+-?\d+$', line):
                toc_lines.append((page_num + 1, line.strip()))

        # Check footer region (last 5 lines)
        footer_lines = text.splitlines()[-5:]
        for line in footer_lines:
            match = re.search(r'(FFIEC|FR\s+Y-9C).*?\s+([A-Z]{1,4}-[A-Z]?-?\d+)', line)
            if match:
                marker = match.group(2)
                label = line.strip()
                if (page_num + 1, label) not in toc_lines:
                    toc_lines.append((page_num + 1, label))

    return toc_lines

def extract_from_ocr(pdf_path, max_pages=15):
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

def extract_page_markers(pdf_path, max_pages=15):
    toc_lines = extract_from_text(pdf_path, max_pages)
    if not toc_lines:
        print("No page markers found via text or footer. Falling back to OCR...")
        toc_lines = extract_from_ocr(pdf_path, max_pages)
    return toc_lines

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract TOC-style and footer markers from PDF.")
    parser.add_argument("pdf_path", help="Path to the input PDF file.")
    parser.add_argument("--max_pages", type=int, default=15, help="Number of initial pages to scan.")
    args = parser.parse_args()

    results = extract_page_markers(args.pdf_path, args.max_pages)

    if results:
        print("\n🧾 Extracted Page Markers (ToC and Footers):")
        for page_num, line in results:
            print(f"[PDF Page {page_num}] {line}")
    else:
        print("❌ No page markers found in the provided PDF.")
