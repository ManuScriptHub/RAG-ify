from fastapi import APIRouter, UploadFile, HTTPException, Header, Depends
from pydantic import BaseModel
from services.text_extractor import extract_text
from services.chunking import chunking
from services.embedding import embed_texts
from typing import List, Optional
import json
import time
from datetime import datetime
from core.config import settings

router = APIRouter()


class ChunkingRequest(BaseModel):
    model: Optional[str] = None
    chunk_size: Optional[int] = None
    overlap: Optional[int] = None
    context: str

class EmbeddingRequest(BaseModel):
    model: str
    texts: List[str]

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
            {"chunkId": i+1, "chunkText": chunk["content"]}
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
        
        embeddings = embed_texts(data.model, data.texts)

        end_time = time.time()
        duration = round(end_time - start_time, 4)
        readable_time = datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S")

        formatted_embeddings = [
            {"embeddingId": i+1, "embeddingValue": emb}
            for i, emb in enumerate(embeddings)
        ]

        return {
            "results": {"embeddings": formatted_embeddings},
            "stats": {"timestamp": readable_time, "duration": duration}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
