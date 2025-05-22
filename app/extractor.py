import re

def build_section_index(text):
    sections = {}
    matches = re.finditer(r"Schedule\s+([A-Z]+)[\—\-–]?\s*(.*?)(?=Schedule\s+[A-Z]+|$)", text, re.DOTALL)
    for match in matches:
        schedule_code = match.group(1).strip()
        schedule_text = match.group(2).strip()
        sections[schedule_code] = schedule_text
    return sections

def extract_line_items(schedule_text):
    items = []
    pattern = r"Line\s+Item\s+(\d+(\([a-z]\))?)\s+(.+?)(?=(?:Line\s+Item\s+\d|\Z))"
    matches = re.finditer(pattern, schedule_text, re.DOTALL)

    for match in matches:
        line_number = match.group(1).strip()
        item_name = match.group(3).strip().replace("\n", " ")
        instructions = match.group(0).strip()

        items.append({
            "Line #": line_number,
            "Item Name": item_name,
            "Report Instructions": instructions,
        })

    return items
