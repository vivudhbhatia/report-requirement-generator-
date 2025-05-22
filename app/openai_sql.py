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

General Instructions:
{row.get('general_instructions', 'N/A')}

Glossary References:
{row.get('glossary', 'N/A')}

ASC References:
{row.get('asc_references', 'N/A')}

Instructions:
Break down the business requirements for this line item. Output in JSON with:
1. Product
2. Logical Data Elements
3. Regulatory Logic (SQL-style pseudocode)
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
