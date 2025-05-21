def generate_sql_requirements(item_details):
    prompt = build_prompt(item_details)  # uses template
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']
