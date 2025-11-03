import time
from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from pydantic import BaseModel

from app.services.ocr_service import ocr_service
from app.core.dependencies_microservice import get_current_user
from app.models.user import User

router = APIRouter()


class OCRResponse(BaseModel):
    words: List[str]
    total_words: int
    processing_time: float


@router.post("/extract", response_model=OCRResponse)
async def extract_words_from_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Extract words from uploaded image
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    start_time = time.time()
    
    try:
        # Read image data
        image_data = await file.read()
        
        # Extract words using OCR
        words = await ocr_service.extract_words_from_image(image_data)
        
        processing_time = time.time() - start_time
        
        return OCRResponse(
            words=words,
            total_words=len(words),
            processing_time=round(processing_time, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process image: {str(e)}")


class Base64OCRRequest(BaseModel):
    image: str


@router.post("/extract-base64", response_model=OCRResponse)
async def extract_words_from_base64(
    request: Base64OCRRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Extract words from base64 encoded image
    """
    start_time = time.time()
    
    try:
        words = await ocr_service.extract_words_from_base64(request.image)
        
        processing_time = time.time() - start_time
        
        return OCRResponse(
            words=words,
            total_words=len(words),
            processing_time=round(processing_time, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process image: {str(e)}")