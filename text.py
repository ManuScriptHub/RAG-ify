import os

from groq import Groq

client = Groq(
    # This is the default and can be omitted
    api_key="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",
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "you are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama-3.3-70b-versatile",
)

print(chat_completion.choices[0].message.content)