import fitz  # PyMuPDF
import pandas as pd
import re


def extract_section_marker_ranges(doc):
    pattern = r'\b((?:[A-Z]{1,4}(?:-[A-Z])?)?-\d{1,2})\b'
    markers = []
    for i, page in enumerate(doc):
        text = page.get_text()
        matches = re.findall(pattern, text)
        for match in matches:
            markers.append((match, i + 1))

    df = pd.DataFrame(markers, columns=["Section Marker", "Page Number"])
    df["Prefix"] = df["Section Marker"].str.extract(r'^([A-Z]{1,4}(?:-[A-Z])?)')
    df["Numeric"] = df["Section Marker"].str.extract(r'-(\d+)').astype(float)

    summary = df.groupby("Prefix")["Numeric"].agg(["min", "max"]).reset_index()
    summary["Start Marker"] = summary["Prefix"] + "-" + summary["min"].astype(int).astype(str)
    summary["End Marker"] = summary["Prefix"] + "-" + summary["max"].astype(int).astype(str)
    summary["Section ID - Name"] = summary["Prefix"]
    return summary[["Section ID - Name", "Start Marker", "End Marker"]]


def find_page_number(doc, marker):
    for i, page in enumerate(doc):
        if marker in page.get_text():
            return i
    return -1


def extract_instructions(doc, section_df):
    rows = []
    for _, row in section_df.iterrows():
        section_name = row["Section ID - Name"]
        start_page = find_page_number(doc, row["Start Marker"])
        end_page = find_page_number(doc, row["End Marker"])
        if start_page == -1 or end_page == -1:
            continue

        text_block = "\n".join(doc.load_page(p).get_text() for p in range(start_page, end_page + 1))

        # Match column or item style instructions
        matches = list(re.finditer(r'(?P<code>(Item|Line|Column)\s+\d+[a-z]?(?:\([a-z0-9]+\))?)[:\.\s-]*', text_block, re.IGNORECASE))

        if not matches:
            # fallback: add the entire section if no matches found
            rows.append({
                "Report Code": "Auto-detected",
                "Report Name": "FFIEC Instruction Report",
                "Report General Instructions": "N/A",
                "Section/Schedule ID - Name": section_name,
                "Section/Schedule General Instructions": "N/A",
                "Line Item Code - Description": "N/A",
                "Column ID - Description": "N/A",
                "Item or Column Instructions": text_block.strip()
            })
            continue

        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text_block)
            instruction = text_block[start:end].strip()
            rows.append({
                "Report Code": "Auto-detected",
                "Report Name": "FFIEC Instruction Report",
                "Report General Instructions": "N/A",
                "Section/Schedule ID - Name": section_name,
                "Section/Schedule General Instructions": "N/A",
                "Line Item Code - Description": match.group("code"),
                "Column ID - Description": match.group("code") if "Column" in match.group("code") else "N/A",
                "Item or Column Instructions": instruction
            })

    return pd.DataFrame(rows)
