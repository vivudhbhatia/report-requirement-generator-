import streamlit as st
import pandas as pd
from app.parser import parse_pdf_from_file
from app.extractor import extract_schedule_line_items
from app.openai_sql import generate_brd_prompt

st.set_page_config(page_title="📄 Universal BRD Extractor", layout="wide")
st.title("📄 Regulatory Report BRD Generator")

uploaded_file = st.file_uploader("Upload Regulatory PDF", type="pdf")
if uploaded_file:
    text, title_text = parse_pdf_from_file(uploaded_file)
    st.success("✅ File parsed")

    auto_report_id = "UNKNOWN"
    if "Y-9C" in title_text:
        auto_report_id = "FR Y-9C"
    elif "FFIEC 002" in title_text:
        auto_report_id = "FFIEC 002"
    elif "FFIEC 009" in title_text:
        auto_report_id = "FFIEC 009"

    report_id = st.text_input("Report ID", value=auto_report_id)
    all_items = extract_schedule_line_items(text, report_id)
    df = pd.DataFrame(all_items)

    schedule_list = sorted(df['schedule'].unique())
    selected_schedule = st.selectbox("Select Schedule/Section", schedule_list)

    filtered = df[df['schedule'] == selected_schedule]
    line_item_list = filtered['line_item'].unique().tolist()
    selected_item = st.selectbox("Select Line Item", line_item_list)

    selected_row = filtered[filtered['line_item'] == selected_item].iloc[0]
    st.markdown(f"**{selected_row['line_title']}**")
    st.text_area("Line Item Instructions", selected_row['instructions'], height=250)

    if st.button("🧠 Generate BRD with OpenAI"):
        response, prompt = generate_brd_prompt(selected_row)
        st.markdown("### 🔍 GPT Output")
        st.code(response)
