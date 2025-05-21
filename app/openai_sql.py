import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_sql(row):
    prompt = f"""
You are a business analyst. Generate SQL for the following instruction:

Instruction: {row['instruction']}

Use hypothetical but consistent data elements and valid values.
Output only the SQL query.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message["content"]

