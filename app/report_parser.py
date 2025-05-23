import fitz  # PyMuPDF
import re
import pandas as pd

def extract_section_marker_ranges(doc):
    pattern = r'\b((GEN|C|L|O|D)-\d{1,2}|App A-\d+)\b'
    markers = []

    for i, page in enumerate(doc):
        text = page.get_text()
        matches = re.findall(pattern, text)
        for match in matches:
            markers.append((match[0], i + 1))

    df = pd.DataFrame(markers, columns=["Section Marker", "Page Number"])
    df["Prefix"] = df["Section Marker"].str.extract(r'^([A-Z]+|App A)')
    df["Numeric"] = df["Section Marker"].str.extract(r'-(\d+)').astype(float)

    summary = df.groupby("Prefix")["Numeric"].agg(["min", "max"]).reset_index()
    summary["Section Name"] = summary["Prefix"].apply(lambda x: f"Section {x}")
    summary["Start Marker"] = summary["Prefix"] + "-" + summary["min"].astype(int).astype(str)
    summary["End Marker"] = summary["Prefix"] + "-" + summary["max"].astype(int).astype(str)

    return summary[["Section Name", "Start Marker", "End Marker"]]

def find_page_number(doc, marker):
    for i, page in enumerate(doc):
        if marker in page.get_text():
            return i
    return -1

def extract_instructions_from_doc(doc, section_df):
    results = []

    for _, row in section_df.iterrows():
        section_name = row["Section Name"]
        start_marker = row["Start Marker"]
        end_marker = row["End Marker"]

        start_page = find_page_number(doc, start_marker)
        end_page = find_page_number(doc, end_marker)

        if start_page == -1 or end_page == -1:
            continue

        text_block = "\n".join(doc.load_page(p).get_text() for p in range(start_page, end_page + 1))

        matches = re.finditer(r'([A-Z]\. )?(.*?)\s*\((Columns \d+.*?|Item .*?)\)', text_block)
        for match in matches:
            intro = match.group(2).strip()
            column_header = match.group(3).strip()
            start = match.start()

            following_text = text_block[start:]
            split = re.split(r'\n[A-Z]\. .*?\(Columns \d+.*?\)', following_text)
            instruction = split[0].strip()

            results.append({
                "Report Code": "FFIEC 009",
                "Report Name": "Country Exposure Report",
                "Report General Instructions": "N/A",
                "Section/Schedule ID - Name": section_name,
                "Section/Schedule General Instructions": "N/A",
                "Line Item Code - Description": "N/A",
                "Column ID - Description": column_header,
                "Item or Column Instructions": instruction
            })

    return pd.DataFrame(results)

# CLI entrypoint
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Extract FFIEC-style instruction data from PDF.")
    parser.add_argument("pdf_path", help="Path to the instruction PDF")
    args = parser.parse_args()

    doc = fitz.open(args.pdf_path)
    marker_df = extract_section_marker_ranges(doc)
    marker_df.to_csv("section_marker_ranges.csv", index=False)

    instruction_df = extract_instructions_from_doc(doc, marker_df)
    instruction_df.to_csv("structured_instructions.csv", index=False)

    print("✅ section_marker_ranges.csv and structured_instructions.csv generated.")
