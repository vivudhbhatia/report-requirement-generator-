import re

def extract_line_items(text):
    pattern = r"(?:MDRM\s*:\s*(?P<mdrm>[A-Z0-9]+))?.*?"               r"Line\s+(?P<line_number>\d+)\s*[-:–]?\s*(?P<item_name>[^\n]+)\n(?P<instruction>.*?)(?=\n\s*Line\s+\d+|\Z)"

    matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
    items = []

    for m in matches:
        items.append({
            "report_id": "FFIEC002_202412",
            "schedule": "UNKNOWN",
            "line_number": m.group("line_number").strip(),
            "item_name": m.group("item_name").strip(),
            "report_instructions": m.group("instruction").strip(),
            "mdrm_name": m.group("mdrm") if m.group("mdrm") else "N/A"
        })

    return items
