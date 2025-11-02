from fastapi import APIRouter

from app.api.v1.endpoints import users, folders, vocabulary, ocr

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(folders.router, prefix="/folders", tags=["folders"])
api_router.include_router(vocabulary.router, prefix="/folders", tags=["vocabulary"])
api_router.include_router(ocr.router, prefix="/ocr", tags=["ocr"])