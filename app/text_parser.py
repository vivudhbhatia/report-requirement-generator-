import fitz
import re

def pdf_to_text(pdf_path):
    with fitz.open(pdf_path) as doc:
        return "\n".join([page.get_text() for page in doc])

def detect_toc_keywords(text, max_lines=300):
    """
    Auto-detect section headers like 'Schedule C, Part I' or 'Schedule HI-A'
    """
    lines = text.splitlines()
    toc_candidates = []
    pattern = re.compile(r"Schedule\s+[A-Z0-9\-]+(?:,\s+Part\s+[IVXLCDM]+)?", re.IGNORECASE)

    for line in lines[:max_lines]:
        if pattern.search(line):
            toc_candidates.append(line.strip())

    return list(dict.fromkeys(toc_candidates))  # remove duplicates, preserve order

def extract_sections_by_toc(text, toc_keywords):
    sections = {}
    lines = text.split("\n")

    toc_indices = {}
    for i, line in enumerate(lines):
        for keyword in toc_keywords:
            if keyword.lower() in line.lower():
                toc_indices[keyword] = i

    sorted_keys = sorted(toc_indices.items(), key=lambda x: x[1])
    for idx, (title, start) in enumerate(sorted_keys):
        end = sorted_keys[idx + 1][1] if idx + 1 < len(sorted_keys) else len(lines)
        sections[title] = "\n".join(lines[start:end]).strip()

    return sections
