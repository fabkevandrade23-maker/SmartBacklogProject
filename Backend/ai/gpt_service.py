from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

def generate_tasks(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Tu es un expert agile"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content