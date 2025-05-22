import streamlit as st
from app.parser import parse_pdf_from_file, parse_pdf_from_url
from app.extractor import extract_line_items
from app.openai_sql import generate_brd
from app.db import save_to_supabase, query_supabase, get_all_line_items, get_failed_queue
import pandas as pd

st.set_page_config(page_title="📄 Report BRD Generator", layout="wide")
st.title("📄 Report Instructions to SQL BRD")

option = st.radio("Choose Input Method", ["📤 Upload PDF", "🔗 Provide URL", "🔁 Reprocess Existing Report"])
text = ""

if option == "📤 Upload PDF":
    uploaded_file = st.file_uploader("Upload Report PDF", type="pdf")
    if uploaded_file:
        text = parse_pdf_from_file(uploaded_file)

elif option == "🔗 Provide URL":
    url = st.text_input("Paste the direct URL to the PDF")
    if url and st.button("Fetch PDF"):
        text = parse_pdf_from_url(url)

elif option == "🔁 Reprocess Existing Report":
    report_id = st.text_input("Enter Report ID to reprocess (e.g., FFIEC002_202412)")
    if st.button("Reprocess Now") and report_id:
        st.info("Fetching entries from Supabase...")
        all_rows = get_all_line_items(report_id)
        re_enriched = []
        for row in all_rows:
            result, prompt, response = generate_brd(row)
            row.update(result)
            save_to_supabase(row, prompt, response)
            re_enriched.append(row)
        df = pd.DataFrame(re_enriched)
        st.success(f"Reprocessed {len(re_enriched)} rows.")
        st.dataframe(df)

if text:
    st.success("✅ PDF parsed successfully.")
    line_items = extract_line_items(text)
    st.info(f"Found {len(line_items)} line items.")

    with st.spinner("Generating SQL BRD using OpenAI..."):
        enriched = []
        for row in line_items:
            result, prompt, response = generate_brd(row)
            row.update(result)
            enriched.append(row)
            save_to_supabase(row, prompt, response)
        df = pd.DataFrame(enriched)
        st.success("All rows processed and saved to Supabase.")
        st.dataframe(df)

    if st.button("Download Current Output"):
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "report_brd_output.csv", "text/csv")

st.divider()
st.subheader("🔍 Search Report BRD Records")
query_term = st.text_input("Enter MDRM, Line Item #, or Item Name")
schedule_filter = st.text_input("Optional: Filter by Schedule")
line_filter = st.text_input("Optional: Filter by Line Number")

if query_term:
    results = query_supabase(query_term)
    if schedule_filter:
        results = [r for r in results if r.get("schedule") == schedule_filter]
    if line_filter:
        results = [r for r in results if r.get("line_number") == line_filter]
    if results:
        st.dataframe(pd.DataFrame(results))
    else:
        st.warning("No results found.")

st.divider()
st.subheader("🔁 Retry Failed Inserts")

failed = get_failed_queue()
if st.button("Show Retry Queue"):
    if failed:
        st.warning(f"{len(failed)} rows failed during last run.")
        st.dataframe(pd.DataFrame(failed))
        retry_csv = pd.DataFrame(failed).to_csv(index=False).encode('utf-8')
        st.download_button("Download Retry Queue as CSV", retry_csv, "retry_queue.csv", "text/csv")
    else:
        st.success("No failed rows to retry.")

if failed and st.button("🔄 Retry All Failed Rows"):
    retry_enriched = []
    for row in failed:
        result, prompt, response = generate_brd(row)
        row.update(result)
        save_to_supabase(row, prompt, response)
        retry_enriched.append(row)
    st.success(f"Retried {len(retry_enriched)} rows.")
    st.dataframe(pd.DataFrame(retry_enriched))

st.divider()
st.subheader("🛠️ Bulk Edit & Resubmit Failed Rows")

if failed:
    edit_df = pd.DataFrame(failed)
    edited = st.data_editor(edit_df, num_rows="dynamic", key="bulk_editor")

    if st.button("Submit Edited Rows"):
        for _, row in edited.iterrows():
            as_dict = row.to_dict()
            prompt = f"Edited manually for line {as_dict['line_number']}"
            response = "Manually updated entry"
            save_to_supabase(as_dict, prompt, response)
        st.success(f"{len(edited)} edited rows submitted to Supabase.")
