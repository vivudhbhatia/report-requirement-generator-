import streamlit as st
from app.parser import parse_pdf_from_file, parse_pdf_from_url
from app.extractor import extract_line_items
from app.openai_sql import generate_brd
from app.db import save_to_supabase, query_supabase
import pandas as pd

st.set_page_config(page_title="📄 Report BRD Generator", layout="wide")
st.title("📄 Report Instructions to SQL BRD")

option = st.radio("Choose Input Method", ["📤 Upload PDF", "🔗 Provide URL"])
text = ""

if option == "📤 Upload PDF":
    uploaded_file = st.file_uploader("Upload Report PDF", type="pdf")
    if uploaded_file:
        text = parse_pdf_from_file(uploaded_file)

elif option == "🔗 Provide URL":
    url = st.text_input("Paste the direct URL to the PDF")
    if url and st.button("Fetch PDF"):
        text = parse_pdf_from_url(url)

if text:
    st.success("✅ PDF parsed successfully.")
    line_items = extract_line_items(text)
    st.info(f"Found {len(line_items)} line items.")

    with st.spinner("Generating SQL BRD using OpenAI..."):
        enriched = []
        for row in line_items:
            result = generate_brd(row)
            row.update(result)
            enriched.append(row)
            save_to_supabase(row)
        df = pd.DataFrame(enriched)
        st.success("All rows processed and saved to Supabase.")
        st.dataframe(df)

    if st.button("Download Current Output"):
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "report_brd_output.csv", "text/csv")

st.divider()
st.subheader("🔍 Search Report BRD Records")
query_term = st.text_input("Enter MDRM, Line Item #, or Item Name")
if query_term:
    results = query_supabase(query_term)
    if results:
        st.dataframe(pd.DataFrame(results))
    else:
        st.warning("No results found.")
