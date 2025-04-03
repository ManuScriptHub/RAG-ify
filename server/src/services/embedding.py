import voyageai
from typing import List

vo = voyageai.Client(api_key="pa-EX4UzuMG41P5EHGTdbSQyCM4LNaqrtkXtCX7gqNWXKe")

def embed_texts(model: str, texts: List[str]):
    """
    Embeds a list of texts using Voyage AI.
    
    Parameters:
    - model: The embedding model (default is "voyage-3-large").
    - texts: A list of strings to be embedded.

    Returns:
    - List of embeddings.
    """
    result = vo.embed(texts, model=model, input_type="query")
    return result.embeddings
