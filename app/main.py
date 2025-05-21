import streamlit as st
from app.parser import parse_pdf
from app.extractor import extract_structure
from app.openai_sql import generate_sql
from app.db import save_report_data

# Set page title and layout
st.set_page_config(page_title="Report → SQL Generator", layout="wide")
st.title("📄 Report Instruction to SQL Generator")
st.markdown("""
Upload a long-form regulatory **PDF report instruction document**.  
The app will extract sections and rows, and generate **SQL business requirements** using OpenAI.
""")

# File uploader
uploaded_file = st.file_uploader("Upload your Report Instruction PDF", type=["pdf"])

if uploaded_file:
    try:
        # Parse the uploaded PDF
        text = parse_pdf(uploaded_file)
        if not text:
            st.warning("⚠️ Unable to extract text from this PDF.")
        else:
            # Extract structured sections and rows
            structure = extract_structure(text)
            st.success("✅ Successfully parsed the document.")

            # Display parsed structure
            st.subheader("📂 Parsed Sections and Rows")
            with st.expander("View parsed structure"):
                st.json(structure)

            # Let user select rows
            row_options = [row["line_item"] for row in structure["rows"]]
            selected_rows = st.multiselect("🧾 Select rows to generate SQL", row_options)

            # Generate SQL
            if st.button("🚀 Generate SQL"):
                for row in structure["rows"]:
                    if row["line_item"] in selected_rows:
                        with st.spinner(f"Generating SQL for {row['line_item']}..."):
                            try:
                                sql = generate_sql(row)
                                st.code(sql, language="sql")
                                save_report_data(row, sql)
                            except Exception as e:
                                st.error(f"❌ Error generating SQL for {row['line_item']}: {e}")
    except Exception as e:
        st.error(f"❌ Failed to process PDF: {e}")

