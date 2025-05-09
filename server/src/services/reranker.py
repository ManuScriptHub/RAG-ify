import voyageai
from typing import List
# from core.config import settings

# voyage = voyageai.Client(api_key=settings.VOYAGE_API_KEY)
voyage = voyageai.Client(api_key="pa-EX4UzuMG41P5EHGTdbSQyCM4LNaqrtkXtCX7gqNWXKe")

def re_rank(query: str, documents: List[str], model: str = "rerank-2", top_k: int = 3):
    """
    Reranks a list of documents based on their relevance to a given query using Voyage AI.

    Parameters:
    - query: The query string.
    - documents: A list of document strings to be reranked.
    - model: The reranking model (default is "rerank-2").
    - top_k: The number of top documents to return (default is 3).

    Returns:
    - A list of reranked documents with their relevance scores.
    """
    print("gggg",query, documents)
    reranking = voyage.rerank(query, documents, model=model, top_k=top_k)
    return reranking.results[:top_k]


print(re_rank("fruits", ["apple","orange", "carrot", "nail"]))