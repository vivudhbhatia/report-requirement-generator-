import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_brd_block(block):
    base_prompt = f"Section: {block['title']}\n\nInstructions:\n{block['text']}"

    if block["type"] == "line_item":
        prompt = base_prompt + "\n\nBreak down each line item into: Product, Logical Data Elements, SQL-like Regulatory Logic."
    elif block["type"] == "column_based":
        prompt = base_prompt + "\n\nExplain the logic for each column and how it maps to product or regulatory requirements. Output as JSON."
    else:
        prompt = base_prompt + "\n\nSummarize business logic and convert it to a structured SQL-like requirement including inferred data elements and valid values."

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        content = response.choices[0].message.content
        return content, prompt
    except Exception as e:
        return f"Error: {str(e)}", prompt
