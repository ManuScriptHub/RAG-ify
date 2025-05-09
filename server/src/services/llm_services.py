import os
from dotenv import load_dotenv
import json

# from groq import Groq

# load_dotenv()
# api_key = os.getenv("GROQ_API_KEY")

# if not api_key:
#     raise ValueError("GROQ_API_KEY not found in environment")

# def llm_service(prompt: str, model: str, context: str = None):
#     try:
#         client = Groq(api_key=api_key)
#         prompt_template = f"{context}\nQuestion: {prompt}\nAnswer:" if context else prompt

#         chat_completion = client.chat.completions.create(
#             messages=[
#                 {"role": "system", "content": "you are a helpful assistant."},
#                 {"role": "user", "content": prompt_template}
#             ],
#             model="llama-3.3-70b-versatile",
#         )

#         result = chat_completion.choices[0].message.content
#         return result if result else "LLM returned no content."

#     except Exception as e:
#         print(f"An error occurred in llm_service: {e}")
#         import traceback
#         traceback.print_exc()
#         return "Sorry, I couldn’t process that request due to an internal error."


from euriai import EuriaiClient

load_dotenv()
api_key = os.getenv("EURIAI_API_KEY")

if not api_key:
    raise ValueError("EURIAI_API_KEY not found in environment")

client = EuriaiClient(
    api_key=api_key,  # Replace with your actual API key
    model="gpt-4.1-mini"
)

def llm_service(
    prompt: str,
    model: str = "gpt-4.1-mini",
    context: str = None,
    return_full_response: bool = False  # << Add this flag
):
    try:
        system_message = "You are a helpful assistant."
        if context:
            prompt_template = f"{system_message}\n\n{context}\n\nQuestion: {prompt}\nAnswer:"
        else:
            prompt_template = f"{system_message}\n\nQuestion: {prompt}\nAnswer:"

        response = client.generate_completion(
            prompt=prompt_template,
            temperature=0.7,
            max_tokens=300
        )

        # Optionally return full response
        if return_full_response:
            return json.dumps(response, indent=2)  # or just `response` if JSON-serializable
        else:
            return response["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"An error occurred in llm_service: {e}")
        return None
