from fastapi import APIRouter, UploadFile, HTTPException
from pydantic import BaseModel
from services.text_extractor import extract_text
from services.chunking import chunking
import json

router = APIRouter()

class ChunkingRequest(BaseModel):
    model: str
    context: str


@router.post("/extractor")
async def upload_file(file: UploadFile):
    try:
        content = await file.read()
        file_type = file.filename.split('.')[-1] if '.' in file.filename else ''


        if not file_type:
            raise HTTPException(status_code=400, detail="Could not determine file type")


        extracted_text = extract_text(file_type, content)

        return {
            "filename": file.filename,
            "file_type": file_type,
            "text_content": extracted_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await file.close()

@router.post("/chunking")
async def chunking_route(data: ChunkingRequest):
    try:
        result = chunking(data.model, data.context)
        # parsed_result = json.loads(result) if isinstance(result, str) else result
        parsed_result = json.loads(result) if isinstance(result, str) else result

        return {
            "result": parsed_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
