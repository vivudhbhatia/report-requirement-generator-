import streamlit as st
from app.parser import parse_pdf_from_file, parse_pdf_from_url
from app.extractor import build_section_index, extract_line_items
from app.openai_sql import generate_brd
from app.db import save_to_supabase
import pandas as pd

st.set_page_config(page_title="📄 Report BRD Generator", layout="wide")
st.title("📄 Report Instructions to SQL BRD")

# Step 1: Load PDF (upload or URL)
option = st.radio("Choose Input Method", ["📤 Upload PDF", "🔗 Provide URL"])
text = ""

try:
    if option == "📤 Upload PDF":
        uploaded_file = st.file_uploader("Upload Report PDF", type="pdf")
        if uploaded_file:
            text = parse_pdf_from_file(uploaded_file)

    elif option == "🔗 Provide URL":
        url = st.text_input("Paste the direct URL to the PDF")
        if url and st.button("Fetch PDF"):
            text = parse_pdf_from_url(url)

    if text:
        st.success("✅ PDF parsed. Building section index...")
        section_index = build_section_index(text)

        selected_section = st.selectbox("📚 Choose Section to Extract", list(section_index.keys()))
        preview = section_index[selected_section][:1500]
        st.text_area(f"Preview: {selected_section}", preview, height=300)

        if st.button("🧠 Extract Business Logic for This Section"):
            line_items = extract_line_items(section_index[selected_section])
            enriched = []
            for row in line_items:
                row["schedule"] = selected_section
                row["report_id"] = "FFIEC002_202412"
                result, prompt, response = generate_brd(row)
                row.update(result)
                save_to_supabase(row, prompt, response)
                enriched.append(row)

            df = pd.DataFrame(enriched)
            st.success(f"✅ Extracted and saved {len(df)} line items.")
            st.dataframe(df)
except Exception as e:
    st.error(f"❌ Error: {e}")
