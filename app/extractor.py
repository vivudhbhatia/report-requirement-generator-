import re

def extract_blocks(text):
    blocks = []
    pattern = re.compile(r"(?P<header>(Schedule\s+[A-Z]+|Part\s+[IVXLC]+|[A-Z]\.\s.*?|\d+\.\s.*?))\n(?P<body>.*?)(?=\n[A-Z]\.\s|\n\d+\.\s|\Z)", re.DOTALL)

    for match in pattern.finditer(text):
        header = match.group("header").strip()
        body = match.group("body").strip()

        if re.search(r"Line\s+\d+|[A-Z]{1,3}\d{3,4}", body):
            block_type = "line_item"
        elif re.search(r"Column\s+\d+", body):
            block_type = "column_based"
        else:
            block_type = "narrative"

        blocks.append({
            "title": header,
            "text": body,
            "type": block_type
        })

    return blocks
