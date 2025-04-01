from fastapi import APIRouter, UploadFile, HTTPException
from services.text_extractor import extract_text
import mimetypes

router = APIRouter()


@router.post("/extractor")
async def upload_file(file: UploadFile):
    try:
        # Read the file content
        content = await file.read()
        
        # Determine file type from the filename
        file_type = file.filename.split('.')[-1] if '.' in file.filename else ''
        
        if not file_type:
            raise HTTPException(status_code=400, detail="Could not determine file type")
        
        # Extract text from the file
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
