import streamlit as st
import tempfile
from app.toc_parser import map_toc_to_page_ranges
from app.extractor import extract_line_or_column_items
from app.openai_sql import decode_line_logic
from app.db import save_to_supabase
import fitz

st.set_page_config(layout="wide")
st.title("📄 ToC-Aware Page-Scoped Regulatory Report Extractor")

if "section_pages" not in st.session_state:
    st.session_state.section_pages = {}

uploaded_file = st.file_uploader("Upload Regulatory PDF", type="pdf")

if uploaded_file and st.button("Extract Sections from ToC"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp.flush()
        toc_map = map_toc_to_page_ranges(tmp.name, max_pages=5)
        st.session_state.section_pages = toc_map
        st.session_state.pdf_path = tmp.name
        st.success(f"✅ Mapped {len(toc_map)} sections from ToC.")

if st.session_state.get("section_pages"):
    selected_section = st.selectbox("Select Section", list(st.session_state.section_pages.keys()))
    start, end = st.session_state.section_pages[selected_section]

    with fitz.open(st.session_state.pdf_path) as doc:
        page_text = "\n".join([doc[i].get_text() for i in range(start, end)])

    rows = extract_line_or_column_items(page_text)

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
                row["Section"] = selected_section
                row["Report"] = uploaded_file.name.split(".pdf")[0]
                save_to_supabase(row)
    else:
        st.warning("⚠️ No line or column items found in this section.")
