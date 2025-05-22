import streamlit as st
import pandas as pd
from app.parser import parse_pdf_from_file
from app.extractor import extract_schedule_line_items
from app.openai_sql import generate_brd_prompt
from app.db import save_brd_row

st.set_page_config(page_title="📄 Schedule + Line Item BRD Generator", layout="wide")
st.title("📄 Schedule + Line Item BRD Extractor")

uploaded_file = st.file_uploader("Upload Regulatory PDF", type="pdf")
if uploaded_file:
    text = parse_pdf_from_file(uploaded_file)
    st.success("✅ File parsed")

    report_id = st.text_input("Enter Report Name (e.g., FR Y-9C)")
    if report_id:
        line_items = extract_schedule_line_items(text, report_id)
        df = pd.DataFrame(line_items)

        selected_schedule = st.selectbox("Select Schedule", sorted(df['schedule'].unique()))
        filtered = df[df['schedule'] == selected_schedule]

        selected_item = st.selectbox("Select Line Item", filtered['line_item'])
        item_row = filtered[filtered['line_item'] == selected_item].iloc[0]

        st.markdown(f"**{item_row['line_title']}**")
        st.text_area("Line Instructions", item_row['instructions'], height=250)

        if st.button("🧠 Generate BRD with OpenAI"):
            response, prompt = generate_brd_prompt(item_row)
            st.markdown("### 🔍 OpenAI Output")
            st.code(response)
            save_brd_row(item_row, prompt, response)
            st.success("✅ Saved to Supabase")
