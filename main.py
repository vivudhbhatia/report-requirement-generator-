import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
import tempfile
import fitz
import pandas as pd
from app import report_parser

st.set_page_config(layout="wide")
st.title("📘 FFIEC Instruction Parser")

uploaded_file = st.file_uploader("Upload an FFIEC PDF Report", type="pdf")

if uploaded_file and st.button("Extract Instruction Table"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp.flush()
        doc = fitz.open(tmp.name)

    with st.spinner("🔍 Extracting section marker ranges..."):
        section_df = report_parser.extract_section_marker_ranges(doc)
        st.success(f"✅ Detected {len(section_df)} unique sections.")

    with st.spinner("📄 Parsing detailed column or item instructions..."):
        result_df = report_parser.extract_instructions(doc, section_df)
        st.success(f"✅ Extracted {len(result_df)} instruction entries.")

        st.dataframe(result_df)

        csv = result_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Extracted CSV", csv, file_name="structured_instructions.csv", mime="text/csv")
