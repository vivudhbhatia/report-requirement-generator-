import re

def build_section_index(text):
    """
    Extract sections by schedule headings like:
    'Schedule RC – Balance Sheet'
    'Schedule HC – Consolidated Balance Sheet'
    """
    sections = {}
    matches = list(re.finditer(r"(Schedule\s+[A-Z0-9\-]+(?:\s[\–\-]\s.*?)?)\n", text))

    for i, match in enumerate(matches):
        header = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end]
        sections[header] = content.strip()

    return sections


def extract_line_items(schedule_text):
    """
    Extracts individual line items from a schedule using flexible matching logic.
    Returns a list of dictionaries with 'Line #', 'Item Name', and 'Report Instructions'
    """
    items = []

    pattern = r"(Line\s+Item\s+\d+[a-zA-Z\(\)]*|Item\s+\d+[a-zA-Z\(\)]*|Line\s+\d+[a-zA-Z\(\)]*)[\.:\-\s]+(.+?)(?=\n(?:Line\s+Item|Item|Line)\s+\d+|\nSchedule\s+|$)"
    matches = re.finditer(pattern, schedule_text, re.DOTALL | re.IGNORECASE)

    for match in matches:
        line_number = match.group(1).strip()
        item_title = match.group(2).strip().replace("\n", " ")
        full_block = match.group(0).strip()

        items.append({
            "Line #": line_number,
            "Item Name": item_title,
            "Report Instructions": full_block
        })

    return items
