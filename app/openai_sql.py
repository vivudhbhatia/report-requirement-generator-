import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def decode_line_logic(row):
    prompt = f"""
You are a regulatory analyst.

Below is an instruction block from a regulatory report.
────────────────────────────────────────────────────────
Report: {row.get('Report', 'UNKNOWN')}
Schedule: {row.get('Schedule', 'UNKNOWN')}
Part: {row.get('Part', 'N/A')}
Section: {row.get('Section', 'N/A')}
Line Item: {row.get('Line #')} – {row.get('Item Name')}

Instructions:
{row.get('Report Instructions')}
────────────────────────────────────────────────────────

Return output in this strict JSON format:

{{
  "Product": "string",
  "Logical_Data_Elements": ["element1", "element2", "..."],
  "Schedule_Level_Filters": {{
    "FILTER_1": "value",
    "FILTER_2": "value"
  }},
  "Regulatory_Logic_Blocks": [
    {{
      "Logic": "SQL-like expression with filters and group by...",
      "Column": "Column number or label"
    }},
    ...
  ]
}}

DO NOT add commentary or explanation. Return only the JSON object.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        result_text = response.choices[0].message.content
        return json.loads(result_text)

    except Exception as e:
        return {
            "Product": "ERROR",
            "Logical_Data_Elements": [],
            "Schedule_Level_Filters": {},
            "Regulatory_Logic_Blocks": [
                {
                    "Logic": f"OpenAI API call failed: {e}",
                    "Column": "N/A"
                }
            ]
        }
