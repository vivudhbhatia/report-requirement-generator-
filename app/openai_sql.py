import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_brd_prompt(row):
    prompt = f"""
You are a regulatory analyst. The following content is from a regulatory report.

Report: {row['report_id']}
Schedule/Section: {row['schedule']}
Line Item: {row['line_item']} – {row['line_title']}

Instructions:
{row['instructions']}

Break down the business requirements into the following JSON format:
{{
  "Product": "...",
  "Logical_Data_Elements": ["..."],
  "Regulatory_Logic": "SELECT ... WHERE ..."
}}
Ensure Regulatory_Logic is SQL-like and uses appropriate filters and data elements.
"""
    try:
        res = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return res.choices[0].message.content, prompt
    except Exception as e:
        return str(e), prompt
