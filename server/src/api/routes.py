from fastapi import APIRouter, Form, UploadFile, HTTPException, Header, Depends, Query
from pydantic import BaseModel
from services.text_extractor import extract_text
from services.chunking import chunking
from services.embedding import get_embedding
from services.reranker import re_rank
from typing import List, Optional
import json
import time
from datetime import datetime
from core.config import settings

from controllers.users import (
    get_users_data, get_user_data, create_user_data, update_user_data, delete_user_data
)

from controllers.corpora import (
    get_corpuses_data, get_corpus_data, create_corpus_data, update_corpus_data, delete_corpus_data
)

from controllers.documents import (
    get_documents_data, get_document_data, create_document_data, update_document_data, delete_document_data
)

from controllers.document_chunk import (
    get_documents_chunks, get_document_chunk, update_document_chunk, create_document_chunk, delete_document_chunk, search_document_chunk
)

from services.process_document import process_document



router = APIRouter()


class ChunkingRequest(BaseModel):
    model: Optional[str] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    text: str
    chunk_type: Optional[str] = "manual"

class EmbeddingRequest(BaseModel):
    model: str
    texts: List[str]

class CreateUserRequest(BaseModel):
    username: str
    email: str
    passwordHash: str
    
class UpdateUserRequest(BaseModel):
    username: Optional[str] = None  
    email: Optional[str] = None    
    passwordHash: Optional[str] = None  

class CreateCorporaRequest(BaseModel):
    userId: str
    corpusKey: str

class UpdateCorporaRequest(BaseModel):
    userId: Optional[str]
    corpusKey: Optional[str]

class CreateDocumentRequest(BaseModel):
    userId: str
    corpusId: int
    docType: str
    docName: str
    sourceUrl: Optional[str] = None
    tags: Optional[List[str]] = None
    rawText: Optional[str] = None

class UpdateDocumentRequest(BaseModel):
    userId: Optional[str] = None
    corpusId: Optional[int] = None
    docType: Optional[str] = None
    docName: Optional[str] = None
    sourceUrl: Optional[str] = None
    tags: Optional[List[str]] = None
    rawText: Optional[str] = None

class UpdateChunkRequest(BaseModel):
    chunkText: Optional[str] = None
    embeddingData: Optional[str] = None
    metadata: Optional[str] = None

class CreateChunkRequest(BaseModel):
    documentId: str
    chunkIndex: int
    chunkText: str
    embeddingData: str
    metaData: Optional[str] = None

class SearchRequest(BaseModel):
    question: str
    top_k: int = 5
    model: Optional[str] = None

class ProcessDocumentRequest(BaseModel):
    corpusKey: str
    userId: str

class RerankRequest(BaseModel):
    query: str
    documents: List[str]
    model: str = "rerank-2"
    top_k: Optional[int] = 3

def api_validation(X_API_KEY: str = Header(...)):
    api_key = settings.API_KEY
    if X_API_KEY != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True

@router.post("/extractor")
async def upload_file(file: UploadFile, api_key: str = Depends(api_validation)):
    try:
        start_time = time.time()
        
        content = await file.read()
        file_type = file.filename.split('.')[-1] if '.' in file.filename else ''

        if not file_type:
            raise HTTPException(status_code=400, detail="Could not determine file type")

        extracted_text = extract_text(file_type, content)

        end_time = time.time()
        duration = round(end_time - start_time, 4)
        readable_time = datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S")

        return {"results": {
            "filename": file.filename,
            "file_type": file_type,
            "text_content": extracted_text,
            "stats": {"timestamp": readable_time, "duration": duration}
        }}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await file.close()

@router.post("/chunking")
async def chunking_route(data: ChunkingRequest, api_key: str = Depends(api_validation)):
    try:
        start_time = time.time()

        chunking_data = data.dict(exclude_none=True)
        result = chunking(chunking_data)

        parsed_result = json.loads(result) if isinstance(result, str) else result

        end_time = time.time()
        duration = round(end_time - start_time, 4)
        readable_time = datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S")

        formatted_chunks = [
            {"chunk_id": i+1, "chunk_text": chunk["content"]}
            for i, chunk in enumerate(parsed_result)
        ]

        return {
            "results": {"chunks": formatted_chunks, 
                        "stats": {"timestamp": readable_time, "duration": duration}},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/embedding")
async def embeddings_route(data: EmbeddingRequest, api_key: str = Depends(api_validation)):
    try:
        start_time = time.time()
        
        embeddings = get_embedding(data.model, data.texts)

        end_time = time.time()
        duration = round(end_time - start_time, 4)
        readable_time = datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S")

        formatted_embeddings = [
            {"embedding_id": i+1, "embedding_value": emb}
            for i, emb in enumerate(embeddings)
        ]

        return {
            "results": {"embeddings": formatted_embeddings, "stats": {"timestamp": readable_time, "duration": duration}}
            
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/users", 
    responses={
        200: {"description": "List of users retrieved successfully"},
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error"},
        503: {"description": "Database connection error"}
    }
)
async def get_users(
    where: str = Query(None, description="JSON string with filter conditions"),
    api_key: str = Depends(api_validation)
):
    """
    Get a list of users with optional filtering.
    
    - **where**: Optional JSON string with filter conditions (e.g., {"username": "john"})
    """
    where_conditions = None
    if where:
        try:
            where_conditions = json.loads(where)
            if not isinstance(where_conditions, dict):
                raise HTTPException(status_code=400, detail="Where conditions must be a JSON object")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in where parameter")
    
    return get_users_data(where_conditions)

@router.get("/user/{userId}", 
    responses={
        200: {"description": "User retrieved successfully"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
        503: {"description": "Database connection error"}
    }
)
async def get_user(
    userId: str, 
    api_key: str = Depends(api_validation)
):
    """
    Get a specific user by ID.
    
    - **userId**: The unique identifier of the user
    """
    return get_user_data(userId)

@router.post('/user', 
    status_code=201,
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Invalid user data"},
        409: {"description": "User already exists"},
        500: {"description": "Internal server error"},
        503: {"description": "Database connection error"}
    }
)
async def create_user(
    request: CreateUserRequest, 
    api_key: str = Depends(api_validation)
):
    """
    Create a new user.
    
    - **username**: Required username for the new user
    - **email**: Email address (optional, default will be used if not provided)
    - **passwordHash**: Required password hash
    """
    user_data_input = request.dict()

    return create_user_data(user_data_input)

@router.put("/user/{userId}", 
    responses={
        200: {"description": "User updated successfully"},
        400: {"description": "Invalid user data"},
        404: {"description": "User not found"},
        409: {"description": "Username already exists"},
        500: {"description": "Internal server error"},
        503: {"description": "Database connection error"}
    }
)
async def update_user(
    request: UpdateUserRequest, 
    userId: str, 
    api_key: str = Depends(api_validation)
):
    """
    Update an existing user.
    
    - **userId**: The unique identifier of the user to update
    - **username**: New username (optional)
    - **email**: New email address (optional)
    - **passwordHash**: New password hash (optional)
    """
    user_data_input = request.dict(exclude_unset=True)
    return update_user_data(user_data_input, userId)

@router.delete("/user/{userId}", 
    responses={
        200: {"description": "User deleted successfully"},
        404: {"description": "User not found"},
        409: {"description": "User cannot be deleted due to references"},
        500: {"description": "Internal server error"},
        503: {"description": "Database connection error"}
    }
)
async def delete_user(
    userId: str, 
    api_key: str = Depends(api_validation)
):
    """
    Delete a user.
    
    - **userId**: The unique identifier of the user to delete
    """
    return delete_user_data(userId)

# corpora routes
@router.get("/corpuses",
    responses={
        200: {"description": "Corpus deleted successfully"},
        404: {"description": "Corpus not found"},
        409: {"description": "Corpus cannot be deleted due to references"},
        500: {"description": "Internal server error"},
        503: {"description": "Database connection error"}
    }
)
async def get_corpuses(
    where: str = Query(None, description="JSON string with filter conditions"),
    api_key: str = Depends(api_validation)
):
    where_conditions = None
    if where:
        try:
            where_conditions = json.loads(where)
            if not isinstance(where_conditions, dict):
                raise HTTPException(status_code=400, detail="Where conditions must be a JSON object")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in where parameter")
    
    return get_corpuses_data(where_conditions)

@router.get("/corpus/{corpusId}",
    responses={
        200: {"description": "Corpus retrieved successfully"},
        404: {"description": "Corpus not found"},
        500: {"description": "Internal server error"},
        503: {"description": "Database connection error"}
    }
)
async def get_corpus(
    corpusId: str, 
    api_key: str = Depends(api_validation)
):
    """
    Get a specific corpus by ID.
    
    - **corpusId**: The unique identifier of the corpus
    """
    return get_corpus_data(corpusId)

@router.post('/corpus',
    status_code=201,
    responses={
        201: {"description": "Corpus created successfully"},
        400: {"description": "Invalid corpus data"},
        409: {"description": "Corpus already exists"},
        500: {"description": "Internal server error"},
        503: {"description": "Database connection error"}
    }
)
async def create_corpus(
    request: CreateCorporaRequest, 
    api_key: str = Depends(api_validation)
):
    """
    Create a new corpus.
    
    - **userId**: The ID of the user who owns this corpus
    - **corpusKey**: A unique key for this corpus
    """
    corpus_data_input = request.dict()
    return create_corpus_data(corpus_data_input)

@router.put('/corpus/{corpusId}',
    responses={
        200: {"description": "Corpus updated successfully"},
        400: {"description": "Invalid corpus data"},
        404: {"description": "Corpus not found"},
        409: {"description": "Corpus key already exists"},
        500: {"description": "Internal server error"},
        503: {"description": "Database connection error"}
    }
)
async def update_corpus(
    request: UpdateCorporaRequest, 
    corpusId: str, 
    api_key: str = Depends(api_validation)
):
    """
    Update an existing corpus.
    
    - **corpusId**: The unique identifier of the corpus to update
    - **userId**: New user ID (optional)
    - **corpusKey**: New corpus key (optional)
    """
    corpus_data_input = request.dict(exclude_unset=True)  # Ensure only provided fields are included
    return update_corpus_data(corpus_data_input, corpusId)

@router.delete('/corpus/{corpusId}',
    responses={
        200: {"description": "Corpus deleted successfully"},
        404: {"description": "Corpus not found"},
        409: {"description": "Corpus cannot be deleted due to references"},
        500: {"description": "Internal server error"},
        503: {"description": "Database connection error"}
    }
)
async def delete_corpus(
    corpusId: str, 
    api_key: str = Depends(api_validation)
):
    """
    Delete a corpus.
    
    - **corpusId**: The unique identifier of the corpus to delete
    """
    return delete_corpus_data(corpusId)

# document routes


@router.get("/documents",
    responses={
        200: {"description": "List of documents retrieved successfully"},
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error"},
        503: {"description": "Database connection error"}
    }
)
async def get_documents(
    where: str = Query(None, description="JSON string with filter conditions"),
    api_key: str = Depends(api_validation)
):
    """
    Get a list of documents with optional filtering.
    
    - **where**: Optional JSON string with filter conditions (e.g., {"userId":"123","docType":"pdf"})
    """
    where_conditions = None
    if where:
        try:
            where_conditions = json.loads(where)
            if not isinstance(where_conditions, dict):
                raise HTTPException(status_code=400, detail="Where conditions must be a JSON object")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in where parameter")
    
    return get_documents_data(where_conditions)

@router.get("/document/{document_id}",
    responses={
        200: {"description": "Document retrieved successfully"},
        404: {"description": "Document not found"},
        500: {"description": "Internal server error"},
        503: {"description": "Database connection error"}
    }
)
async def get_document(
    document_id: str, 
    api_key: str = Depends(api_validation)
):
    """
    Get a specific document by ID.
    
    - **document_id**: The unique identifier of the document
    """
    return get_document_data(document_id)

@router.post("/document",
    status_code=201,
    responses={
        201: {"description": "Document created successfully"},
        400: {"description": "Invalid document data"},
        500: {"description": "Internal server error"},
        503: {"description": "Database connection error"}
    }
)
async def create_document(
    request: CreateDocumentRequest, 
    api_key: str = Depends(api_validation)
):
    """
    Create a new document.
    
    - **userId**: The ID of the user who owns this document
    - **corpusId**: The ID of the corpus this document belongs to
    - **docType**: The type of document (e.g., "pdf", "docx", "url")
    - **docName**: The name of the document
    - **sourceUrl**: Optional URL source of the document
    - **tags**: Optional tags for the document
    - **rawText**: Optional raw text content of the document
    """
    document_input_data = request.dict()
    return create_document_data(document_input_data)

@router.put("/document/{docId}",
    responses={
        200: {"description": "Document updated successfully"},
        400: {"description": "Invalid document data"},
        404: {"description": "Document not found"},
        500: {"description": "Internal server error"},
        503: {"description": "Database connection error"}
    }
)
async def update_document(
    request: UpdateDocumentRequest, 
    docId: str, 
    api_key: str = Depends(api_validation)
):
    """
    Update an existing document.
    
    - **docId**: The unique identifier of the document to update
    - **userId**: New user ID (optional)
    - **corpusId**: New corpus ID (optional)
    - **docType**: New document type (optional)
    - **docName**: New document name (optional)
    - **sourceUrl**: New source URL (optional)
    - **tags**: New tags (optional)
    - **rawText**: New raw text content (optional)
    """
    document_data_input = request.dict(exclude_none=True)  # Ensure only provided fields are included
    return update_document_data(document_data_input, docId)

@router.delete("/document/{document_id}",
    responses={
        200: {"description": "Document deleted successfully"},
        404: {"description": "Document not found"},
        500: {"description": "Internal server error"},
        503: {"description": "Database connection error"}
    }
)
async def delete_document(
    document_id: str, 
    api_key: str = Depends(api_validation)
):
    """
    Delete a document.
    
    - **document_id**: The unique identifier of the document to delete
    """
    return delete_document_data(document_id)


@router.get("/chunks",
    responses={
        200: {"description": "List of document chunks retrieved successfully"},
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error"},
        503: {"description": "Database connection error"}
    }
)
async def get_documents_chunks_data(
    where: str = Query(None, description="JSON string with filter conditions"),
    api_key: str = Depends(api_validation)
):
    """
    Get a list of document chunks with optional filtering.
    
    - **where**: Optional JSON string with filter conditions (e.g., {"documentId": "doc123"})
    """
    where_conditions = None
    if where:
        try:
            where_conditions = json.loads(where)
            if not isinstance(where_conditions, dict):
                raise HTTPException(status_code=400, detail="Where conditions must be a JSON object")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in where parameter")
    
    return get_documents_chunks(where_conditions)

@router.get("/chunk/{chunk_id}",
    responses={
        200: {"description": "Document chunk retrieved successfully"},
        404: {"description": "Document chunk not found"},
        500: {"description": "Internal server error"},
        503: {"description": "Database connection error"}
    }
)
async def get_document_chunk_data(
    chunk_id: str, 
    api_key: str = Depends(api_validation)
):
    """
    Get a specific document chunk by ID.
    
    - **chunk_id**: The unique identifier of the document chunk
    """
    return get_document_chunk(chunk_id)

@router.put("/chunk/{chunk_id}",
    responses={
        200: {"description": "Document chunk updated successfully"},
        400: {"description": "Invalid chunk data"},
        404: {"description": "Document chunk not found"},
        500: {"description": "Internal server error"},
        503: {"description": "Database connection error"}
    }
)
async def update_document_chunk_data(
    chunk_id: str, 
    request: UpdateChunkRequest, 
    api_key: str = Depends(api_validation)
):
    """
    Update an existing document chunk.
    
    - **chunk_id**: The unique identifier of the document chunk to update
    - **chunkText**: New chunk text (optional)
    - **embeddingData**: New embedding data (optional)
    - **metadata**: New metadata (optional)
    """
    chunk_input_data = request.dict(exclude_none=True)
    return update_document_chunk(chunk_id, chunk_input_data)

@router.post("/chunk",
    status_code=201,
    responses={
        201: {"description": "Document chunk created successfully"},
        400: {"description": "Invalid chunk data"},
        500: {"description": "Internal server error"},
        503: {"description": "Database connection error"}
    }
)
async def create_document_chunk_data(
    request: CreateChunkRequest, 
    api_key: str = Depends(api_validation)
):
    """
    Create a new document chunk.
    
    - **documentId**: The ID of the parent document
    - **chunkIndex**: The index of this chunk within the document
    - **chunkText**: The text content of the chunk
    - **embeddingData**: The embedding data (will be generated if not provided)
    - **metaData**: Optional metadata for the chunk
    """
    chunk_input_data = request.dict()
    return create_document_chunk(chunk_input_data)

@router.delete("/chunk/{chunk_id}",
    responses={
        200: {"description": "Document chunk deleted successfully"},
        404: {"description": "Document chunk not found"},
        500: {"description": "Internal server error"},
        503: {"description": "Database connection error"}
    }
)
async def delete_document_chunk_data(
    chunk_id: str, 
    api_key: str = Depends(api_validation)
):
    """
    Delete a document chunk.
    
    - **chunk_id**: The unique identifier of the document chunk to delete
    """
    return delete_document_chunk(chunk_id)

@router.post("/search",
    responses={
        200: {"description": "Search completed successfully"},
        400: {"description": "Invalid search parameters"},
        500: {"description": "Internal server error"}
    }
)
async def search_document_chunk_data(
    request: SearchRequest, 
    api_key: str = Depends(api_validation)
):
    """
    Search for document chunks relevant to a question.
    
    - **question**: The search query
    - **top_k**: Maximum number of results to return (default: 5)
    - **model**: The embedding model to use (optional)
    """
    return search_document_chunk(request.question, request.top_k, request.model)

@router.post("/process/document")
async def process_document_data(
    file: Optional[UploadFile] = None,
    url: Optional[str] = Form(None),
    corpus_key: str = Form(...),
    userId: str = Form(...),
    api_key: str = Depends(api_validation)
):
    try:
        print(file)
        if not file and not url:
            raise HTTPException(status_code=400, detail="Either a file or a URL must be provided.")

        if file:
            file_bytes = await file.read()
            file_type = file.filename.split(".")[-1]
            file_name = file.filename.split("/")[-1]  # Use full filename for file_name
            extracted_text = process_document(userId, file_type, file_bytes, corpus_key, file_name)
            print("Received API call to /process/document")
            print("File:", file)
            print("UserId:", userId)
            print("Corpus Key:", corpus_key)

        elif url:
            file_type = "url"
            file_name = url.split("/")[-1]  # Extract file name from the URL
            extracted_text = process_document(userId, file_type, url, corpus_key, file_name)

        return {
            "results": extracted_text["results"],
        }

    except Exception as e:
        print(f"🔥 Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rerank")
async def rerank_documents(request: RerankRequest, api_key: str = Depends(api_validation)):
    try:
        response = re_rank(request.query, request.documents, request.model, request.top_k)
        return {"results": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))