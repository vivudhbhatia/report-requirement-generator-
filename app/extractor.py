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
    # Flexible pattern for "Line Item", "Item", or numbered labels
    pattern = r"(Line\s+Item\s+\d+[a-zA-Z\(\)]*|Item\s+\d+[a-zA-Z\(\)]*)[\.:\-\s]+(.+?)(?=\n(Line\s+Item|Item)\s+\d+|\nSchedule\s+|$)"
    matches = re.finditer(pattern, schedule_text, re.DOTALL | re.IGNORECASE)

    for match in matches:
        label = match.group(1).strip()
        title = match.group(2).strip().replace("\n", " ")
        full_block = match.group(0).strip()

        items.append({
            "Line #": label,
            "Item Name": title,
            "Report Instructions": full_block
        })

    return items
