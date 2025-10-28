from fastapi import APIRouter

from app.api.v1.endpoints import users, folders, vocabulary

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(folders.router, prefix="/folders", tags=["folders"])
api_router.include_router(vocabulary.router, prefix="/folders", tags=["vocabulary"])