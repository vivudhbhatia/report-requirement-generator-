import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def decode_line_logic(row):
    prompt = f"""Extract the PRODUCT, LOGICAL DATA ELEMENTS, and SQL-LIKE REGULATORY LOGIC from the instruction below:

---
INSTRUCTION:
{row['Report Instructions']}
---

Return result in this format:
{{
    "Product": "...",
    "Logical Data Elements": ["...", "..."],
    "Regulatory Logic": "SELECT ... WHERE ..."
}}"""

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
