import re

def extract_schedule_line_items(text, report_id="UNKNOWN"):
    schedule_pattern = re.compile(r"(Schedule\s+[A-Z0-9\-\.]+|Section\s+[A-Z0-9]+|Part\s+[A-Z]+)", re.IGNORECASE)
    line_item_pattern = re.compile(r"(Line\sItem\s+\d+[a-zA-Z\(\)]*|Item\s+\d+[a-zA-Z\(\)]*)[\.\-\:]?\s+(.+?)\n(.*?)(?=\n(Line\sItem|Item)\s+\d+|\nSchedule\s+|\nSection\s+|\Z)", re.DOTALL)

    all_blocks = []
    matches = list(schedule_pattern.finditer(text))

    for i, match in enumerate(matches):
        schedule = match.group(1).strip()
        start = match.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        block_text = text[start:end]

        item_matches = list(line_item_pattern.finditer(block_text))
        if not item_matches:
            all_blocks.append({
                "report_id": report_id,
                "schedule": schedule,
                "line_item": "N/A",
                "line_title": "No line items detected",
                "instructions": block_text.strip()
            })
        for m in item_matches:
            all_blocks.append({
                "report_id": report_id,
                "schedule": schedule,
                "line_item": m.group(1).strip(),
                "line_title": m.group(2).strip(),
                "instructions": m.group(3).strip()
            })

    return all_blocks
