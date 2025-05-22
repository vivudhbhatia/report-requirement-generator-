import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_brd_prompt(row):
    prompt = f"""
Report: {row['report_id']}
Schedule: {row['schedule']}
Line Item: {row['line_item']} – {row['line_title']}

Instructions:
{row['instructions']}

Please return the business requirements as a JSON object with these fields:
- "Product": tentative product
- "Logical_Data_Elements": list of data elements used
- "Regulatory_Logic": SQL-style logic using those elements and valid values

Example output format:
{{
  "Product": "Trust Preferred Securities",
  "Logical_Data_Elements": ["instrument_type", "issuer_type", "maturity"],
  "Regulatory_Logic": "SELECT SUM(amount) FROM liabilities WHERE instrument_type = 'trust preferred' AND issuer_type IN ('unconsolidated_spe', 'consolidated_spe')"
}}
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
