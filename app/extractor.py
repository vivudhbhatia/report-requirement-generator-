import re

def extract_line_or_column_items(text_block):
    """
    Extracts line items from ToC-based text block using flexible patterns:
    - Line Item 5(b)
    - Item 4.
    - Column 3:
    - Col 2
    - Bullet points (optional enhancement)
    """
    pattern = r"(Line\s+Item\s+\d+[a-zA-Z\(\)]*|Item\s+\d+[a-zA-Z\(\)]*|Column\s+\d+[a-zA-Z\(\)]*|Col\s+\d+[a-zA-Z\(\)]*)[\.\-:\s]+(.+?)(?=\n(?:Line\s+Item|Item|Column|Col)\s+\d+|\n[A-Z][a-z]+\s+[A-Z][a-z]+|\n\*\s|$)"
    matches = re.finditer(pattern, text_block, re.DOTALL | re.IGNORECASE)
    items = []

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
