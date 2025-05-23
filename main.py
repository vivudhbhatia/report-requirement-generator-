import streamlit as st
import tempfile
import fitz
import pandas as pd
from app import report_parser

st.set_page_config(layout="wide")
st.title("📊 FFIEC Instruction Extractor")

uploaded_file = st.file_uploader("Upload an FFIEC PDF", type="pdf")

if uploaded_file and st.button("Extract Instructions"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp.flush()
        doc = fitz.open(tmp.name)

    with st.spinner("🔍 Detecting section marker ranges..."):
        marker_df = report_parser.extract_section_marker_ranges(doc)
        st.success("✅ Section marker ranges extracted.")

    with st.spinner("📄 Extracting detailed instructions..."):
        instruction_df = report_parser.extract_instructions_from_doc(doc, marker_df)
        st.success(f"✅ Extracted {len(instruction_df)} rows.")

        st.dataframe(instruction_df)

        csv = instruction_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, file_name="structured_instructions.csv", mime="text/csv")
