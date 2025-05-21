import re

def extract_structure(text):
    # Placeholder logic
    sections = re.findall(r"Section\s+[A-Z]+.*", text)
    rows = [{"line_item": f"Line {1000 + i}", "instruction": f"Instruction for row {i}"} for i in range(1, 4)]

    return {
        "sections": sections,
        "rows": rows
    }

