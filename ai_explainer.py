from openai import OpenAI

client = OpenAI()

def generate_ai_explanation(repo_summary):

    prompt = f"""
You are an AI software analyst.

Explain the following GitHub repository in a simple human friendly way.

Repository description:
{repo_summary}

Explain:
1. What the project likely does
2. What technologies it uses
3. Who might use this project
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system","content":"You explain software repositories clearly."},
            {"role":"user","content":prompt}
        ]
    )

    return response.choices[0].message.content