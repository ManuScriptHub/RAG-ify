from models.document_chunk import DocumentChunkModel
from services.embedding import get_embedding
from services.llm_services import llm_service
from services.reranker import re_rank
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

documents_data = DocumentChunkModel()

def get_documents_chunks(where_conditions=None):
    response = documents_data.get_document_chunks(where_conditions)
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    # Ensure response has a "results" key with a list value
    if "results" in response and not isinstance(response["results"], list):
        response["results"] = [response["results"]] if response["results"] is not None else []
    
    return response

def get_document_chunk(chunk_id):
    response = documents_data.get_document_chunk(chunk_id)
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    if not response or not response.get("results"):
        raise HTTPException(status_code=404, detail=f"Document chunk with ID {chunk_id} not found")
    
    # Ensure response has a "results" key with a list value
    if "results" in response and not isinstance(response["results"], list):
        response["results"] = [response["results"]] if response["results"] is not None else []
    
    return response

def create_document_chunk(chunk_input_data):
    try:
        # Validate required fields
        if not chunk_input_data:
            raise HTTPException(status_code=400, detail="Chunk data is required")
            
        if "chunkText" not in chunk_input_data or not chunk_input_data["chunkText"]:
            raise HTTPException(status_code=400, detail="Chunk text is required")
            
        if "documentId" not in chunk_input_data or not chunk_input_data["documentId"]:
            raise HTTPException(status_code=400, detail="Document ID is required")
            
        # Generate embedding for the chunkText
        try:
            chunk_input_data["embeddingData"] = get_embedding("voyage-3-large", [chunk_input_data["chunkText"]])[0]
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to generate embedding: {str(e)}")
        
        response = documents_data.create_document_chunk(chunk_input_data)
        
        if "error" in response:
            status_code = response.get("status_code", 500)
            raise HTTPException(status_code=status_code, detail=response["error"])
        
        # Ensure response has a "results" key with a list value
        if "results" in response and not isinstance(response["results"], list):
            response["results"] = [response["results"]] if response["results"] is not None else []
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_document_chunk: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create document chunk: {str(e)}")

def update_document_chunk(chunk_id, chunk_input_data):
    if not chunk_id:
        raise HTTPException(status_code=400, detail="Chunk ID is required")
        
    if not chunk_input_data:
        raise HTTPException(status_code=400, detail="No data provided for update")
    
    response = documents_data.update_document_chunk(chunk_id, chunk_input_data)
    
    if "error" in response:
        status_code = response.get("status_code", 500)
        raise HTTPException(status_code=status_code, detail=response["error"])
    
    # Ensure response has a "results" key with a list value
    if "results" in response and not isinstance(response["results"], list):
        response["results"] = [response["results"]] if response["results"] is not None else []
    
    return response

def delete_document_chunk(chunk_id):
    if not chunk_id:
        raise HTTPException(status_code=400, detail="Chunk ID is required")
        
    success = documents_data.delete_document_chunk(chunk_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Document chunk with ID {chunk_id} not found")
    
    return {"results": [{"message": "Document chunk deleted successfully"}]}

def search_document_chunk(question, top_k, model):
    if not question:
        raise HTTPException(status_code=400, detail="Search question is required")
        
    if not model:
        raise HTTPException(status_code=400, detail="Embedding model is required")
    
    try:
        # Generate embedding for the question
        question_embedding = get_embedding(model, [question])
        if not question_embedding or len(question_embedding) == 0:
            raise HTTPException(status_code=500, detail="Failed to generate embedding for the question")
            
        question_embedding = question_embedding[0]
        
        # Search for relevant chunks
        chunks = documents_data.search_document_chunk(question_embedding, top_k)
        
        if not chunks or len(chunks) == 0:
            return {"results": ["No relevant information found for your question."]}
        
        # Extract text from chunks for reranking
        re_ranker_data = []
        for chunk in chunks:
            re_ranker_data.append(chunk["chunkText"])
        
        # Rerank the results
        try:
            re_rank_result = re_rank(question, re_ranker_data, top_k=top_k)
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            # Fall back to original chunks if reranking fails
            context = "\n\n\n".join([chunk["chunkText"] for chunk in chunks[:2]])
        else:
            # Build context from reranked results
            context = ""
            for result in re_rank_result:
                context += result[1] + "\n\n\n"
        
        # Save context for debugging (optional)
        try:
            with open("test.txt", "w", encoding="utf-8") as file:
                file.write(context)
        except Exception as e:
            logger.warning(f"Failed to write context to file: {e}")
        
        # Generate response using LLM
        prompt = f"""
        question: {question}
        You are a helpful assistant, your task is to summarize the given context of information.

        data: {context}

        If the data is not sufficient to provide an answer, just strictly reply with "Not enough context to provide information."
        """
        
        try:
            result = llm_service(prompt, "", "this is a data about some information")
            return {"results": [result], "chunks": re_rank_result}
        except Exception as e:
            logger.error(f"LLM service failed: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in search_document_chunk: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
