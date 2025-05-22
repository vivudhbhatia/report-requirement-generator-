import fitz
import re

def extract_toc_page_labels(pdf_path, max_pages=5):
    toc_entries = []
    with fitz.open(pdf_path) as doc:
        for page_index in range(min(max_pages, len(doc))):
            text = doc[page_index].get_text()
            lines = text.split("\n")
            for line in lines:
                if re.search(r"Schedule\s+[A-Z0-9\-]+", line):
                    match = re.match(r"(Schedule.*?)\s+\.{{2,}}\s+(\S+)$", line.strip())
                    if match:
                        section, label = match.groups()
                        toc_entries.append((section.strip(), label.strip()))
    return toc_entries

def resolve_label_to_page_index(doc, target_label):
    for i in range(len(doc)):
        if doc[i].get_label() == target_label:
            return i
    return None

def map_toc_to_page_ranges(pdf_path, max_pages=5):
    with fitz.open(pdf_path) as doc:
        toc_raw = extract_toc_page_labels(pdf_path, max_pages)
        toc_mapped = {}
        for i, (section, label) in enumerate(toc_raw):
            start_index = resolve_label_to_page_index(doc, label)
            if start_index is None:
                continue
            end_index = None
            if i + 1 < len(toc_raw):
                next_label = toc_raw[i + 1][1]
                end_index = resolve_label_to_page_index(doc, next_label)
            else:
                end_index = len(doc)
            toc_mapped[section] = (start_index, end_index)
        return toc_mapped
