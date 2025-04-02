from services.llm_services import llm_service

def chunking(model: str, context: str):
    prompt = """Split the given text into chunks of approximately 200–300 words each. Each chunk should be numbered sequentially starting from 1, and the output must be returned as a structured JSON array in the following format:

[
  {
    "chunk_number": 1,
    "content": "First chunk of the text here..."
  },
  {
    "chunk_number": 2,
    "content": "Second chunk of the text here..."
  }
]

Make sure:
- Chunks do NOT break sentences mid-way.
- Logical flow is preserved.
- No extra commentary—just the raw JSON output.

Text will be provided separately."""

    result = llm_service(prompt, model, context)
    return result
