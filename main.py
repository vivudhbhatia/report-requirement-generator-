import streamlit as st
import tempfile
from app.parser import extract_text_blocks
from app.extractor import build_section_index, extract_line_items
from app.openai_sql import decode_line_logic
from app.db import save_to_supabase
import os

st.set_page_config(layout="wide")
st.title("📄 Regulatory Report Extractor & Logic Generator")

option = st.radio("Choose Input Method", ["📁 Upload PDF", "🔗 Provide URL"])

if option == "📁 Upload PDF":
    uploaded = st.file_uploader("Upload FFIEC/FR Y PDF", type="pdf")
    if uploaded and st.button("Extract"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded.read())
            tmp.flush()
            text = extract_text_blocks(tmp.name)

        section_index = build_section_index(text)
        selected_schedule = st.selectbox("Select Schedule", list(section_index.keys()))

        if selected_schedule:
            rows = extract_line_items(section_index[selected_schedule])
            selected_line = st.selectbox("Select Line Item", [r["Line #"] for r in rows])
            row = next((r for r in rows if r["Line #"] == selected_line), None)

            if row:
                st.subheader(f"🧠 AI-Decoded SQL Logic for Line {selected_line}")
                decoded = decode_line_logic(row)
                st.json(decoded)
                row.update(decoded)
                row["Schedule"] = selected_schedule
                row["Report"] = uploaded.name.split(".pdf")[0]
                save_to_supabase(row)
