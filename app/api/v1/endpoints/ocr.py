from typing import List, Dict, Any
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel

from app.services.ocr_service import ocr_service

router = APIRouter()


class WordDetail(BaseModel):
    word: str
    confidence: float
    bbox: List[List[float]]


class TimingInfo(BaseModel):
    total_time_ms: float
    ocr_time_ms: float
    processing_time_ms: float


class OCRResponse(BaseModel):
    words: List[str]
    word_details: List[WordDetail]
    total_words: int
    unique_words: int
    average_confidence: float
    timing: TimingInfo


@router.post("/extract-words", response_model=OCRResponse)
async def extract_words_from_image(file: UploadFile = File(...)):
    """
    Extract words from uploaded image
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image data
        image_data = await file.read()
        
        # Extract words using OCR
        result = await ocr_service.extract_words_from_image(image_data)
        
        return OCRResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process image: {str(e)}")


class Base64OCRRequest(BaseModel):
    image: str


@router.post("/extract-words-base64", response_model=OCRResponse)
async def extract_words_from_base64(request: Base64OCRRequest):
    """
    Extract words from base64 encoded image
    """
    try:
        result = await ocr_service.extract_words_from_base64(request.image)
        return OCRResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process image: {str(e)}")