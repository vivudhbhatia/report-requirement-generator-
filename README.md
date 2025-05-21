# report-requirement-generator-

# Report Instruction to SQL Generator

This Streamlit app ingests long-form regulatory report instruction PDFs and generates SQL business logic for selected row items using OpenAI GPT-4.

## Features
- Upload PDFs or parse from URLs
- Extract report > section > row hierarchy
- Generate SQL with consistent data elements/values
- Optionally extend with Pinecone or FAISS for memory

## Deployment (Streamlit Cloud)
1. Fork or clone this repo
2. Add `.streamlit/secrets.toml` with your OpenAI key:
```toml
OPENAI_API_KEY = "your-key"
