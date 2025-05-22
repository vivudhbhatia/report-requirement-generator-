import streamlit as st
from app.parser import parse_pdf_from_file, parse_pdf_from_url
from app.extractor import extract_blocks
from app.openai_sql import generate_brd_block
import pandas as pd

st.set_page_config(page_title="📄 Report BRD Generator", layout="wide")
st.title("📄 Report Instructions to SQL BRD")

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
        st.success("✅ PDF parsed. Extracting instruction blocks...")
        blocks = extract_blocks(text)
        st.session_state["blocks"] = blocks

        selected_indices = st.multiselect("Select blocks to process", options=list(range(len(blocks))),
                                          format_func=lambda i: f"{blocks[i]['title']} ({blocks[i]['type']})")

        if selected_indices:
            results = []
            for i in selected_indices:
                block = blocks[i]
                st.markdown(f"### 🧠 Generating for: {block['title']} ({block['type']})")
                st.text_area("Instruction Text", block["text"], height=200)
                response, prompt = generate_brd_block(block)
                results.append({
                    "section": block["title"],
                    "type": block["type"],
                    "logic": response,
                    "prompt": prompt
                })
                st.markdown("#### 💡 Extracted Logic")
                st.code(response)

            df = pd.DataFrame(results)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Results as CSV", csv, "brd_output.csv", "text/csv")

except Exception as e:
    st.error(f"❌ Error: {e}")
