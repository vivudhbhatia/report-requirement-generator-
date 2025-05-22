import fitz
import re

def extract_toc_entries(pdf_path, max_pages=15):
    toc_entries = []
    with fitz.open(pdf_path) as doc:
        for page_index in range(min(max_pages, len(doc))):
            text = doc[page_index].get_text()
            lines = text.split("\n")
            for line in lines:
                if "Schedule" in line:
                    # Match formats like:
                    # Schedule C – Balance Sheet ..... A-1
                    # Schedule HC—Consolidated Balance Sheet     HC-1
                    match = re.match(r"(Schedule\s+[A-Z0-9\-]+(?:\s*[–—\-]\s*.*?)?)\s+\.*\s*(\S+)$", line.strip())
                    if not match:
                        match = re.match(r"(Schedule\s+[A-Z0-9\-]+.*?)\s+(\S+)$", line.strip())
                    if match:
                        section, label = match.groups()
                        toc_entries.append((section.strip(), label.strip()))
    return toc_entries

def resolve_label_to_page_index(doc, target_label):
    # Build reverse map of label -> page index
    label_to_index = {doc[i].get_label(): i for i in range(len(doc))}
    return label_to_index.get(target_label)

def map_toc_to_page_ranges(pdf_path, max_pages=15):
    with fitz.open(pdf_path) as doc:
        toc_raw = extract_toc_entries(pdf_path, max_pages)
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
