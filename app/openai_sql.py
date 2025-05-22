import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def decode_line_logic(row):
    prompt = f"""
You are a regulatory analyst. Below is a line item from a regulatory report.

Report: {row.get('Report', 'UNKNOWN')}
Schedule: {row.get('Schedule', 'UNKNOWN')}
Line Item: {row['Line #']} – {row['Item Name']}

Instructions:
{row['Report Instructions']}

Generate a JSON object with:
- "Product": what product this applies to
- "Logical_Data_Elements": list of data fields used in logic
- "Regulatory_Logic": a SQL-style logic statement using the data elements and valid values

Output only the JSON:
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return eval(response.choices[0].message.content)
    except Exception as e:
        return {
            "Product": "Error",
            "Logical_Data_Elements": [],
            "Regulatory_Logic": str(e)
        }
