import streamlit as st
import tempfile
import pandas as pd
from app.extract_page_markers import extract_page_markers
from app.extract_instruction_table import parse_toc_from_lines, extract_section_and_line_items

st.set_page_config(layout="wide")
st.title("📄 PDF Instruction Extractor with Footer-Aware TOC")

uploaded_file = st.file_uploader("Upload a Regulatory PDF", type="pdf")

if uploaded_file and st.button("Extract Table"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp.flush()
        pdf_path = tmp.name

    with st.spinner("🔍 Scanning ToC and footers for section markers..."):
        toc_lines = extract_page_markers(pdf_path, max_pages=15)
        if not toc_lines:
            st.error("❌ No markers found in ToC or footers.")
        else:
            st.success(f"✅ Found {len(toc_lines)} markers (ToC or footer-based).")
            toc_entries = parse_toc_from_lines(toc_lines)

            with st.spinner("📄 Extracting line item instructions..."):
                df = extract_section_and_line_items(pdf_path, toc_entries)
                st.success(f"✅ Extracted {len(df)} entries.")
                st.dataframe(df)

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Download as CSV", csv, file_name="extracted_instruction_table.csv", mime="text/csv")
