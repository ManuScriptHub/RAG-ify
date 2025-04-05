import voyageai
from typing import List
from core.config import settings

voyage = voyageai.Client(api_key=settings.VOYAGE_API_KEY)

def embed_texts(model: str, texts: List[str]):
    """
    Embeds a list of texts using Voyage AI.
    
    Parameters:
    - model: The embedding model (default is "voyage-3-large").
    - texts: A list of strings to be embedded.

    Returns:
    - List of embeddings.
    """
    result = voyage.embed(texts, model=model, input_type="query")
    return result.embeddings
