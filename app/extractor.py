import re

def extract_schedule_line_items(text, report_id):
    schedule_pattern = re.compile(r"(Schedule\s+[A-Z]+(?:-[A-Z]+)?)", re.IGNORECASE)
    line_item_pattern = re.compile(r"(Line\sItem\s+\d+[a-zA-Z\(\)]*)[\.\-\:]?\s+(.+?)\n(.*?)(?=\nLine\sItem\s+\d+|\nSchedule\s+[A-Z]|\Z)", re.DOTALL)

    schedules = schedule_pattern.findall(text)
    all_blocks = []
    seen = set()

    for match in schedule_pattern.finditer(text):
        schedule = match.group(1).strip()
        if schedule in seen:
            continue
        seen.add(schedule)
        start = match.start()
        next_match = next((m for m in schedule_pattern.finditer(text, start + 1)), None)
        end = next_match.start() if next_match else len(text)
        block_text = text[start:end]

        matches = list(line_item_pattern.finditer(block_text))
        if not matches:
            all_blocks.append({
                "report_id": report_id,
                "schedule": schedule,
                "line_item": "N/A",
                "line_title": "No line items detected",
                "instructions": block_text.strip()
            })
        for m in matches:
            all_blocks.append({
                "report_id": report_id,
                "schedule": schedule,
                "line_item": m.group(1).strip(),
                "line_title": m.group(2).strip(),
                "instructions": m.group(3).strip()
            })

    return all_blocks
