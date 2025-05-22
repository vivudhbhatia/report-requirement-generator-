import streamlit as st
import tempfile
from app.parser import extract_text_blocks
from app.extractor import build_schedule_part_index, extract_line_items
from app.openai_sql import decode_line_logic
from app.db import save_to_supabase

st.set_page_config(layout="wide")
st.title("📄 Layout-Aware Regulatory Report Extractor")

if "structure" not in st.session_state:
    st.session_state.structure = {}

uploaded_file = st.file_uploader("Upload Regulatory PDF", type="pdf")

if uploaded_file and st.button("Extract"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp.flush()
        text = extract_text_blocks(tmp.name)

    st.session_state.structure = build_schedule_part_index(text)
    st.success("✅ PDF structure loaded.")

if st.session_state.structure:
    selected_schedule = st.selectbox("Select Schedule", list(st.session_state.structure.keys()))
    selected_part = st.selectbox("Select Part", list(st.session_state.structure[selected_schedule].keys()))
    selected_section = st.selectbox("Select Section", list(st.session_state.structure[selected_schedule][selected_part].keys()))

    block = st.session_state.structure[selected_schedule][selected_part][selected_section]
    rows = extract_line_items(block)

    if rows:
        selected_line = st.selectbox("Select Line Item", [r["Line #"] for r in rows])
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
                row["Schedule"] = selected_schedule
                row["Part"] = selected_part
                row["Section"] = selected_section
                row["Report"] = uploaded_file.name.split(".pdf")[0]
                save_to_supabase(row)
    else:
        st.warning("⚠️ No line items found in this section.")
