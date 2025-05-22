import re

def extract_schedule_line_items(text, report_id):
    schedule_pattern = r"(Schedule\s+[A-Z]+(?:-[A-Z]+)?)"
    line_item_pattern = r"(Line\sItem\s+\d+[a-zA-Z\(\)]*)[\.\-\:]?\s+(.+?)\n(.*?)(?=\nLine\sItem\s+\d+|\nSchedule\s+[A-Z]|\Z)"

    schedules = re.findall(schedule_pattern, text)
    results = []

    for schedule in set(schedules):
        schedule_blocks = text.split(schedule)
        for block in schedule_blocks[1:]:
            for m in re.finditer(line_item_pattern, block, re.DOTALL):
                results.append({
                    "report_id": report_id,
                    "schedule": schedule.strip(),
                    "line_item": m.group(1).strip(),
                    "line_title": m.group(2).strip(),
                    "instructions": m.group(3).strip(),
                })
    return results
