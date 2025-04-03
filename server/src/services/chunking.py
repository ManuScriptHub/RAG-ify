# chunking.py
from services.llm_services import llm_service
import json

def simple_chunking(text: str, chunk_size: int, overlap: int):
    if not text:
        raise ValueError("Context text is empty for manual chunking.")
    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap if end - overlap > start else end
    return [{"chunk_number": i+1, "content": chunk} for i, chunk in enumerate(chunks)]

def chunking(data: dict):
    if "model" in data and "context" in data:  # Use LLM-based chunking
        prompt = f"""Split the following text into chunks of approximately 200–300 words each. Each chunk should be numbered sequentially starting from 1. The output must be returned as a structured JSON array in the following format:

        [
          {{
            "chunk_number": 1,
            "content": "First chunk of the text here..."
          }},
          {{
            "chunk_number": 2,
            "content": "Second chunk of the text here..."
          }}
        ]

        Make sure:
        - Chunks do NOT break sentences mid-way.
        - Logical flow is preserved.
        - No extra commentary—just the raw JSON output.

        Text: {data["context"]}
        """
        
        response = llm_service(prompt, data["model"], data["context"])
        
        if not response or not response.strip():
            raise ValueError("LLM returned an empty response.")
        
        try:
            parsed_response = json.loads(response)
            return parsed_response
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON from LLM: {response}")
    
    elif "chunk_size" in data and "overlap" in data and "context" in data:  # Use manual chunking
        return simple_chunking(data.get("context", ""), data.get("chunk_size", 0), data.get("overlap", 0))
    
    else:
        raise ValueError("Invalid input format. Provide either 'model' with 'context' or 'chunk_size', 'overlap', and 'context'.")
