from fastapi import Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.repositories.user_repo import UserRepository
from app.repositories.product_repo import ProductRepository
from app.services.user_service import UserService
from app.services.product_service import ProductService

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    user_repo = UserRepository(db)
    return UserService(user_repo)

def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    product_repo = ProductRepository(db)
    return ProductService(product_repo)