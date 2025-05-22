import re

def build_section_index(text):
    sections = {}
    current_section = None

    for line in text.splitlines():
        match = re.match(r"(Schedule\s+[A-Z]+(?:-[A-Z]+)?)\s*[-–]?\s*(.+)?", line.strip())
        if match:
            current_section = match.group(1).strip()
            sections[current_section] = ""
        elif current_section:
            sections[current_section] += line + "\n"

    return sections

def extract_line_items(section_text):
    pattern = r"(Line\s+(\d+))[:\s\-]+(.+?)(?=\nLine\s+\d+|\Z)"
    matches = re.finditer(pattern, section_text, re.DOTALL | re.IGNORECASE)
    items = []

    for m in matches:
        items.append({
            "line_number": m.group(2).strip(),
            "item_name": m.group(3).strip(),
            "report_instructions": m.group(0).strip()
        })

    return items
