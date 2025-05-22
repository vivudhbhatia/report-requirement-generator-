import re

def build_schedule_part_index(text):
    """
    Extracts blocks by Schedule > Part > Section hierarchy if present
    """
    structure = {}
    schedule_pattern = re.compile(r"(Schedule\s+[A-Z0-9\-]+.*?)\n", re.IGNORECASE)
    part_pattern = re.compile(r"(Part\s+[IVXLCDM]+(?:\s[–-]\s.*?)?)\n", re.IGNORECASE)
    section_pattern = re.compile(r"(Section\s+[A-Z0-9\.\-]+.*?)\n", re.IGNORECASE)

    schedule_blocks = list(schedule_pattern.finditer(text))
    for i, sched_match in enumerate(schedule_blocks):
        sched_title = sched_match.group(1).strip()
        start = sched_match.end()
        end = schedule_blocks[i+1].start() if i+1 < len(schedule_blocks) else len(text)
        sched_text = text[start:end]

        parts = {}
        part_blocks = list(part_pattern.finditer(sched_text)) or [None]
        for j, part_match in enumerate(part_blocks):
            part_title = part_match.group(1).strip() if part_match else "N/A"
            p_start = part_match.end() if part_match else 0
            p_end = part_blocks[j+1].start() if j+1 < len(part_blocks) else len(sched_text)
            part_text = sched_text[p_start:p_end]

            sections = {}
            section_blocks = list(section_pattern.finditer(part_text)) or [None]
            for k, sec_match in enumerate(section_blocks):
                sec_title = sec_match.group(1).strip() if sec_match else "N/A"
                s_start = sec_match.end() if sec_match else 0
                s_end = section_blocks[k+1].start() if k+1 < len(section_blocks) else len(part_text)
                sec_text = part_text[s_start:s_end]
                sections[sec_title] = sec_text.strip()

            parts[part_title] = sections
        structure[sched_title] = parts

    return structure


def extract_line_items(text_block):
    """
    Extract line items from a block using flexible regex
    """
    pattern = r"(Line\s+Item\s+\d+[a-zA-Z\(\)]*|Item\s+\d+[a-zA-Z\(\)]*|Line\s+\d+[a-zA-Z\(\)]*)[\.:\-\s]+(.+?)(?=\n(?:Line\s+Item|Item|Line)\s+\d+|\\nSchedule\s+|$)"
    matches = re.finditer(pattern, text_block, re.DOTALL | re.IGNORECASE)
    items = []

    for match in matches:
        label = match.group(1).strip()
        title = match.group(2).strip().replace("\n", " ")
        block = match.group(0).strip()
        items.append({
            "Line #": label,
            "Item Name": title,
            "Report Instructions": block
        })

    return items
