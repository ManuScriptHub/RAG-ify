from services.llm_services import llm_service
import json

def chunking(data: dict):
    try:
        context = data.get("text", "")
        if not context:
            raise ValueError("Context text is required.")

        chunk_type = data.get("chunk_type", "manual")

        if chunk_type == "auto":
            model = data.get("model")
            if not model:
                raise ValueError("Model is required for LLM-based chunking.")

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

            Text: {context}
            """

            response = llm_service(prompt, model, context)

            if not response or not response.strip():
                raise ValueError("LLM returned an empty response.")

            try:
                parsed_response = json.loads(response)
                return parsed_response
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON from LLM: {response}")

        elif chunk_type == "manual":
            chunk_size = data.get("chunk_size")
            chunk_overlap = data.get("chunk_overlap", 0)

            if chunk_size is None or chunk_size <= 0:
                raise ValueError("Chunk size must be provided and greater than zero for manual chunking.")

            # Split context into lines
            words = context.split()
            chunks = []
            start = 0

            while start < len(words):
                end = start + chunk_size
                chunk_words = words[start:end]
                chunk_text = " ".join(chunk_words)
                chunks.append(chunk_text)

                # Move start forward, allowing for overlap
                start = end - chunk_overlap if end - chunk_overlap > start else end

            return [{"chunk_number": i + 1, "content": chunk} for i, chunk in enumerate(chunks)]

        else:
            raise ValueError("Invalid chunk_type. Must be 'auto' or 'manual'.")

    except Exception as e:
        raise ValueError(f"An error occurred during chunking: {str(e)}")
