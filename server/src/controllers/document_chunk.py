from models.document_chunk import DocumentChunkModel
from services.embedding import get_embedding
from services.llm_services import llm_service

documents_data = DocumentChunkModel()

def get_documents_chunks():
    documents = documents_data.get_document_chunks()
    result = [dict(document) for document in documents]
    return result

def get_document_chunk(chunk_id):
    document = documents_data.get_document_chunk(chunk_id)
    if document:
        return dict(document)
    return {"error": "Document not found"}

def create_document_chunk(chunk_data):
    chunk_id = documents_data.create_document_chunk(chunk_data)
    if chunk_id:
        return {"message": "Document chunk created successfully", "chunkId": chunk_id}
    return {"error": "Failed to create document chunk"}

def update_document_chunk(chunk_id, updates):
    success = documents_data.update_document_chunk(chunk_id, updates)
    if success:
        return {"message": "Document updated successfully"}
    return {"error": "Document not found"}

def delete_document_chunk(chunk_id):
    success = documents_data.delete_document_chunk(chunk_id)
    if success:
        return {"message": "Document deleted successfully"}
    return {"error": "Document not found"}

def search_document_chunk(question, top_k, model):
    question_embedding = get_embedding(model, question)
    question_embedding = question_embedding[0]
    if question_embedding is None: 
        return {"error": "Failed to get embedding"}
    success = documents_data.search_document_chunk(question_embedding, top_k)
    context = ""
    for chunk in success:
        context += chunk["chunkText"] + "\n\n\n"
    prompt = f"""

    question: {question}
       You are a helpful assistant, your task is to summarize the given context of information.

    data :  {context}

    if the data is not suffiecient to provide answer, just strictly reply with not enough context to provide information.
    """
    result = llm_service(prompt, "", "this is a data about some information")

    if success:
        return {"message": "Search completed successfully", "results": result}
    return {"error": "Search failed"}
