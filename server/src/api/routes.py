from fastapi import APIRouter, UploadFile, HTTPException, Header, Depends
from pydantic import BaseModel
from services.text_extractor import extract_text
from services.chunking import chunking
from services.embedding import get_embedding
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


router = APIRouter()

class ChunkingRequest(BaseModel):
    model: Optional[str] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    context: str

class EmbeddingRequest(BaseModel):
    model: str
    texts: List[str]

class CreateUserRequest(BaseModel):
    username: str
    email: str
    
class UpdateUserRequest(BaseModel):
    username: Optional[str] = ""
    email: Optional[str] = ""
    password: Optional[str] = ""

class CreateCorporaRequest(BaseModel):
    user_id: str
    corpus_key: str

class UpdateCorporaRequest(BaseModel):
    user_id: str
    corpus_key: str

class CreateDocumentRequest(BaseModel):
    userId: str
    corpusId: int
    docType: str
    docName: str
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

        return {
            "filename": file.filename,
            "file_type": file_type,
            "text_content": extracted_text,
            "stats": {"timestamp": readable_time, "duration": duration}
        }
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
            "results": {"chunks": formatted_chunks},
            "stats": {"timestamp": readable_time, "duration": duration}
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
            "results": {"embeddings": formatted_embeddings},
            "stats": {"timestamp": readable_time, "duration": duration}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/users")
async def get_users(api_key: str = Depends(api_validation)):
    return get_users_data()

@router.get("/user/{user_id}")
async def get_user(user_id, api_key: str = Depends(api_validation)):
    return get_user_data(user_id)



@router.post('/user')
async def create_user(request: CreateUserRequest, api_key: str = Depends(api_validation)):
    return create_user_data(request.username, request.email)


@router.put("/user/{user_id}")
async def update_user(request: UpdateUserRequest, user_id, api_key: str = Depends(api_validation)):
    return update_user_data(user_id, request.username, request.email, request.password)

@router.delete("/user/{user_id}")
async def delete_user(user_id: str, api_key: str = Depends(api_validation)):
    return delete_user_data(user_id)



# corpora routes
@router.get("/corpuses")
async def get_corpuses(api_key: str = Depends(api_validation)):
    return get_corpuses_data()

@router.get("/corpus/{corpus_id}")
async def get_corpus(corpus_id, api_key: str = Depends(api_validation)):
    return get_corpus_data(corpus_id)

@router.post('/corpus')
async def create_corpus(request: CreateCorporaRequest,  api_key: str = Depends(api_validation)):
    return create_corpus_data(request.user_id, request.corpus_key)

@router.put('/corpus')
async def update_corpus(request: UpdateCorporaRequest,  api_key: str = Depends(api_validation)):
    return update_corpus_data(request.user_id, request.corpus_key)

@router.delete('/corpus/{corpus_id}')
async def delete_corpus(corpus_id: str, api_key: str = Depends(api_validation)):
    return delete_corpus_data(corpus_id)

# document routes
@router.get("/documents")
async def get_documents(api_key: str = Depends(api_validation)):
    return get_documents_data()

@router.get("/document/{document_id}")
async def get_document(document_id: str, api_key: str = Depends(api_validation)):
    return get_document_data(document_id)

@router.post("/document")
async def create_document(request: CreateDocumentRequest, api_key: str = Depends(api_validation)):
    document_data = request.dict()
    return create_document_data(document_data)

@router.put("/document/{document_id}")
async def update_document(document_id: str, updates: dict, api_key: str = Depends(api_validation)):
    return update_document_data(document_id, updates)

@router.delete("/document/{document_id}")
async def delete_document(document_id: str, api_key: str = Depends(api_validation)):
    return delete_document_data(document_id)


@router.get("/chunks")
async def get_documents_chunks_data(api_key: str = Depends(api_validation)):
    return get_documents_chunks()

@router.get("/chunk/{chunk_id}")
async def get_document_chunk_data(chunk_id: str, api_key: str = Depends(api_validation)):
    return get_document_chunk(chunk_id)

@router.put("/chunk/{chunk_id}")
async def update_document_chunk_data(chunk_id: str, request: UpdateChunkRequest, api_key: str = Depends(api_validation)):
    updates = request.dict(exclude_none=True)
    print(updates)
    return update_document_chunk(chunk_id, updates)

@router.post("/chunk")
async def create_document_chunk_data(request: CreateChunkRequest, api_key: str = Depends(api_validation)):
    chunk_data = request.dict()
    return create_document_chunk(chunk_data)

@router.delete("/chunk/{chunk_id}")
async def delete_document_chunk_data(chunk_id: str, api_key: str = Depends(api_validation)):
    return delete_document_chunk(chunk_id)  


@router.post("/search")
async def search_document_chunk_data(request: SearchRequest, api_key: str = Depends(api_validation)):
    return search_document_chunk(request.question, request.top_k, request.model)
