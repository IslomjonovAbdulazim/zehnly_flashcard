from typing import List
from fastapi import APIRouter, Depends, status

from app.api.deps import get_product_service
from app.core.dependencies import get_current_user
from app.core.exceptions import APIException
from app.core.error_codes import ErrorCode
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.product_service import ProductService
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    product_service: ProductService = Depends(get_product_service),
    current_user: User = Depends(get_current_user)
):
    return await product_service.create_product(product_data)

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 10,
    product_service: ProductService = Depends(get_product_service)
):
    return await product_service.get_products(skip=skip, limit=limit)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(
    product_id: int,
    product_service: ProductService = Depends(get_product_service)
):
    product = await product_service.get_product_by_id(product_id)
    if not product:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=ErrorCode.PRODUCT_NOT_FOUND
        )
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    product_service: ProductService = Depends(get_product_service),
    current_user: User = Depends(get_current_user)
):
    return await product_service.update_product(product_id, product_data)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    product_service: ProductService = Depends(get_product_service),
    current_user: User = Depends(get_current_user)
):
    await product_service.delete_product(product_id)