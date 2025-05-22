import fitz
import re

def extract_toc_entries(pdf_path, max_pages=15):
    toc_entries = []
    with fitz.open(pdf_path) as doc:
        for page_index in range(min(max_pages, len(doc))):
            text = doc[page_index].get_text()
            lines = text.split("\n")
            for line in lines:
                if "Schedule" in line or "Appendix" in line:
                    # Match formats like:
                    # Schedule HC—Balance Sheet .................... HC-1
                    # Appendix A—Summary of Reporting .............. App A-1
                    match = re.match(r"(Schedule\s+[A-Z0-9\-]+(?:\s*[–—\-]\s*.*?)?|Appendix\s+[A-Z0-9]+.*?)\s+\.*\s*(\S+)$", line.strip())
                    if not match:
                        match = re.match(r"(Schedule\s+[A-Z0-9\-]+.*?|Appendix\s+[A-Z0-9]+.*?)\s+(\S+)$", line.strip())
                    if match:
                        section, label = match.groups()
                        toc_entries.append((section.strip(), label.strip()))
    return toc_entries

def resolve_label_to_page_index(doc, target_label):
    label_to_index = {doc[i].get_label(): i for i in range(len(doc))}
    return label_to_index.get(target_label)

def map_toc_to_page_ranges(pdf_path, max_pages=15):
    with fitz.open(pdf_path) as doc:
        toc_raw = extract_toc_entries(pdf_path, max_pages)
        if not toc_raw:
            return None  # fallback triggered if no ToC detected

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

def fallback_all_schedules(pdf_path):
    # Return list of pages where 'Schedule' occurs, just split every 5 pages
    with fitz.open(pdf_path) as doc:
        sections = {}
        current_section = None
        for i in range(len(doc)):
            text = doc[i].get_text()
            if re.search(r"Schedule\s+[A-Z0-9]", text):
                title_match = re.search(r"(Schedule\s+[A-Z0-9\-]+.*?)\n", text)
                title = title_match.group(1) if title_match else f"Schedule at Page {i+1}"
                if current_section:
                    sections[current_section] = (sections[current_section][0], i)
                current_section = title
                sections[current_section] = (i, len(doc))  # will close later
        return sections
