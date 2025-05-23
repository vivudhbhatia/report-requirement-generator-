import fitz  # PyMuPDF
import pandas as pd
import re


def extract_section_marker_ranges(doc):
    # Match patterns like GEN-1, HC-N-5, App A-1
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
    summary["Section ID - Name"] = summary["Prefix"]  # dynamic, no hardcoding

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
        start_marker = row["Start Marker"]
        end_marker = row["End Marker"]

        start_page = find_page_number(doc, start_marker)
        end_page = find_page_number(doc, end_marker)
        if start_page == -1 or end_page == -1:
            continue

        text_block = "\n".join(doc.load_page(p).get_text() for p in range(start_page, end_page + 1))

        matches = re.finditer(
    r'(?P<desc>.*?)\s*\((?P<code>Column[s]?\s+\d+[a-zA-Z\-–, ]*|Item\s+\d+[a-zA-Z\-–()]*)\)',
    text_block
)

        for match in matches:
            groups = match.groupdict()
            column_header = groups.get("code", "").strip()
            description = groups.get("desc", "").strip()
            start = match.start()
        
            following_text = text_block[start:]
            split = re.split(r'\n(?:[A-Z]\. )?.*?\((?:Columns?|Item)\s+\d+[a-zA-Z\-–, ()]*\)', following_text)
            instruction = split[0].strip()
        
            rows.append({
                "Report Code": "Auto-detected",
                "Report Name": "FFIEC Instruction Report",
                "Report General Instructions": "N/A",
                "Section/Schedule ID - Name": section_name,
                "Section/Schedule General Instructions": "N/A",
                "Line Item Code - Description": description or "N/A",
                "Column ID - Description": column_header or "N/A",
                "Item or Column Instructions": instruction or "N/A"
            })



    return pd.DataFrame(rows)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Extract FFIEC Instruction Content Dynamically")
    parser.add_argument("pdf_path", help="Path to FFIEC instruction PDF")
    args = parser.parse_args()

    doc = fitz.open(args.pdf_path)
    section_df = extract_section_marker_ranges(doc)
    section_df.to_csv("section_marker_ranges.csv", index=False)

    instruction_df = extract_instructions(doc, section_df)
    instruction_df.to_csv("structured_instructions.csv", index=False)

    print("✅ section_marker_ranges.csv and structured_instructions.csv saved.")
