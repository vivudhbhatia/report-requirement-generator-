import fitz  # PyMuPDF
import re
import pandas as pd
import argparse
from app.extract_page_markers import extract_page_markers  # Assumes you import from the other script

def parse_toc_from_lines(toc_lines):
    toc = []
    for _, line in toc_lines:
        match = re.search(r'(.*?)\.{3,}\s*(\w+-?\d+)$', line)
        if match:
            title = match.group(1).strip()
            code = match.group(2).strip()
            toc.append((code, title))
    return toc

def extract_section_and_line_items(pdf_path, toc_entries, max_pages=100):
    doc = fitz.open(pdf_path)
    results = []

    for i, (code, name) in enumerate(toc_entries):
        start_page = find_page_by_marker(doc, code, max_pages)
        end_page = find_page_by_marker(doc, toc_entries[i+1][0], max_pages) if i+1 < len(toc_entries) else len(doc)

        text_block = "\n".join([doc.load_page(p).get_text() for p in range(start_page, end_page)])
        line_items = re.findall(r'Item\s+(\d+[a-zA-Z]?(?:\([a-z0-9]+\))?):?\s*(.*?)\n', text_block)

        if not line_items:
            results.append({
                "Section Code": code,
                "Section Name": name,
                "General Instruction": text_block.strip(),
                "Line Item Code": "",
                "Line Item Description": "",
                "Line Item Instruction": ""
            })
        else:
            for match in line_items:
                item_code, description = match
                item_pattern = re.escape("Item " + item_code)
                instruction_match = re.search(rf'{item_pattern}.*?\n(.*?)(?=Item \d+[a-zA-Z]?\(|\Z)', text_block, re.DOTALL)
                instruction = instruction_match.group(1).strip() if instruction_match else ""
                results.append({
                    "Section Code": code,
                    "Section Name": name,
                    "General Instruction": "",
                    "Line Item Code": item_code,
                    "Line Item Description": description.strip(),
                    "Line Item Instruction": instruction
                })

    return pd.DataFrame(results)

def find_page_by_marker(doc, marker, max_pages):
    for i in range(min(max_pages, len(doc))):
        text = doc.load_page(i).get_text()
        if marker in text:
            return i
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract line item instructions from PDF.")
    parser.add_argument("pdf_path", help="Path to the input PDF.")
    parser.add_argument("--max_toc_pages", type=int, default=6, help="Number of pages to scan for TOC.")
    args = parser.parse_args()

    toc_lines = extract_page_markers(args.pdf_path, args.max_toc_pages)
    toc_entries = parse_toc_from_lines(toc_lines)
    df = extract_section_and_line_items(args.pdf_path, toc_entries)
    df.to_csv("extracted_instruction_table.csv", index=False)
    print("✅ Instruction table saved as extracted_instruction_table.csv")
