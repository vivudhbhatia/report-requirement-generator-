import streamlit as st
import tempfile
from app.text_parser import pdf_to_text, detect_toc_keywords, extract_sections_by_toc
from app.extractor import extract_line_or_column_items
from app.openai_sql import decode_line_logic
from app.db import save_to_supabase

st.set_page_config(layout="wide")
st.title("📄 Dynamic ToC-Based Regulatory Report Extractor")

if "toc_sections" not in st.session_state:
    st.session_state.toc_sections = {}

uploaded_file = st.file_uploader("Upload Regulatory PDF", type="pdf")

if uploaded_file and st.button("Extract"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp.flush()
        text = pdf_to_text(tmp.name)

    toc_keywords = detect_toc_keywords(text)
    sections = extract_sections_by_toc(text, toc_keywords)
    st.session_state.toc_sections = sections
    st.success(f"✅ Extracted {len(sections)} sections using detected ToC.")

if st.session_state.toc_sections:
    selected_block = st.selectbox("Select Section", list(st.session_state.toc_sections.keys()))
    text_block = st.session_state.toc_sections[selected_block]
    rows = extract_line_or_column_items(text_block)

    if rows:
        selected_line = st.selectbox("Select Line/Column", [r["Line #"] for r in rows])
        row = next((r for r in rows if r["Line #"] == selected_line), None)

        if row:
            st.subheader(f"🧠 SQL Logic for {selected_line}")
            st.text_area("Line Instructions", row["Report Instructions"], height=200)

            if st.button("Generate BRD"):
                decoded = decode_line_logic(row)
                st.markdown("### 🧩 GPT Output")
                st.json(decoded)

                st.markdown("#### 🔍 Schedule-Level Filters")
                if decoded.get("Schedule_Level_Filters"):
                    filters = "\n".join(f"{k} = '{v}'" for k, v in decoded["Schedule_Level_Filters"].items())
                    st.code(filters, language="sql")
                else:
                    st.markdown("_No schedule-level filters_")

                st.markdown("#### 🧠 Logic Blocks")
                for block in decoded.get("Regulatory_Logic_Blocks", []):
                    col = block.get("Column", "N/A")
                    logic = block.get("Logic", "-- missing logic --")
                    st.markdown(f"**{col}**")
                    st.code(logic, language="sql")

                row.update(decoded)
                row["Section"] = selected_block
                row["Report"] = uploaded_file.name.split(".pdf")[0]
                save_to_supabase(row)
    else:
        st.warning("⚠️ No line or column items found in this section.")
