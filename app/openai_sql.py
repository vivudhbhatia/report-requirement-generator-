import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_brd(row):
    prompt = f"""
Line Item: {row['item_name']}
Schedule: {row['schedule']}
Instructions: {row['report_instructions']}

Break down the above into:
1. Product (tentative)
2. Logical Data Elements (comma-separated)
3. SQL-like Regulatory Logic using those elements and valid values

Return in JSON with keys: product, logical_data_elements, regulatory_logic
"""
    try:
        res = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        msg = res['choices'][0]['message']['content']
        json_output = eval(msg)
        return json_output
    except Exception as e:
        return {
            "product": "Error",
            "logical_data_elements": [],
            "regulatory_logic": str(e)
        }
