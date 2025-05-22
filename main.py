import streamlit as st
import tempfile
from app.parser import extract_text_blocks
from app.extractor import build_section_index, extract_line_items
from app.openai_sql import decode_line_logic  # ← Updated import
from app.db import save_to_supabase
import os

st.set_page_config(layout="wide")
st.title("📄 Regulatory Report Extractor & Logic Generator")

if "section_index" not in st.session_state:
    st.session_state.section_index = {}

if "line_items_by_schedule" not in st.session_state:
    st.session_state.line_items_by_schedule = {}

uploaded_file = st.file_uploader("Upload Regulatory PDF", type="pdf")

if uploaded_file and st.button("Extract"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp.flush()
        text = extract_text_blocks(tmp.name)

    section_index = build_section_index(text)
    st.session_state.section_index = section_index
    st.session_state.line_items_by_schedule = {
        sched: extract_line_items(section_index[sched])
        for sched in section_index
    }
    st.success("✅ PDF parsed and schedules loaded.")

if st.session_state.get("section_index"):
    selected_schedule = st.selectbox("Select Schedule", list(st.session_state.section_index.keys()))

    rows = st.session_state.line_items_by_schedule.get(selected_schedule, [])
    if rows:
        selected_line = st.selectbox("Select Line Item", [r["Line #"] for r in rows])
        row = next((r for r in rows if r["Line #"] == selected_line), None)

        if row:
            st.subheader(f"🧠 AI-Decoded SQL Logic for Line {selected_line}")
            st.text_area("Line Instructions", row["Report Instructions"], height=200)

            if st.button("Generate BRD"):
                decoded = decode_line_logic(row)
                st.markdown("### 🔍 GPT Output")
                st.json(decoded)
                row.update(decoded)
                row["Schedule"] = selected_schedule
                row["Report"] = uploaded_file.name.split(".pdf")[0]
                save_to_supabase(row)
