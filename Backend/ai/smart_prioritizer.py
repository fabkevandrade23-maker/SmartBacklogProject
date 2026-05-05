from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

client = OpenAI()

def prioritize(tasks):
    prompt = f"Classe ces tâches par priorité : {tasks}"

    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content
