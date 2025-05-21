import re

def extract_line_items(text):
    sections = re.split(r"(Schedule\s+[A-Z]+)", text)
    items = []
    for i in range(1, len(sections), 2):
        schedule = sections[i].strip()
        section_text = sections[i+1]
        matches = re.findall(r"(Line\s+\d+)[^\n]*\n(.*?)(?=\nLine\s+\d+|\Z)", section_text, re.DOTALL)
        for m in matches:
            items.append({
                "schedule": schedule,
                "line_number": m[0],
                "item_name": m[0],
                "report_instructions": m[1].strip(),
                "report_id": "FFIEC002_202412"
            })
    return items
