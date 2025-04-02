import os

from groq import Groq


def llm_service(prompt: str, model: str, context: str):
    client = Groq(
        api_key="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",
    )

    prompt_template = f"{context}\nQuestion: {prompt}\nAnswer:"

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "you are a helpful assistant."
            },
            {
                "role": "user",
                "content": f"{prompt_template}",
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    return chat_completion.choices[0].message.content