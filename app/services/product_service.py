from typing import List, Optional
from fastapi import status

from app.core.exceptions import APIException
from app.core.error_codes import ErrorCode
from app.repositories.product_repo import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate
from app.models.product import Product

class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    async def create_product(self, product_data: ProductCreate) -> Product:
        existing_product = self.product_repo.get_by_sku(product_data.sku)
        if existing_product:
            raise APIException(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code=ErrorCode.SKU_ALREADY_EXISTS
            )

        product_dict = product_data.dict()
        return self.product_repo.create_product(product_dict)

    async def get_products(self, skip: int = 0, limit: int = 10) -> List[Product]:
        return self.product_repo.get_active_products(skip=skip, limit=limit)

    async def get_product_by_id(self, product_id: int) -> Optional[Product]:
        return self.product_repo.get_by_id(product_id)

    async def get_product_by_sku(self, sku: str) -> Optional[Product]:
        return self.product_repo.get_by_sku(sku)

    async def update_product(self, product_id: int, product_data: ProductUpdate) -> Product:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=ErrorCode.PRODUCT_NOT_FOUND
            )

        update_data = product_data.dict(exclude_unset=True)
        return self.product_repo.update_product(product, update_data)

    async def delete_product(self, product_id: int) -> bool:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                error_code=ErrorCode.PRODUCT_NOT_FOUND
            )
        
        return self.product_repo.delete(product_id)

    async def search_products(self, search_term: str, skip: int = 0, limit: int = 10) -> List[Product]:
        return self.product_repo.search_products(search_term, skip=skip, limit=limit)

    async def get_products_by_price_range(self, min_price: float, max_price: float, skip: int = 0, limit: int = 10) -> List[Product]:
        return self.product_repo.get_products_by_price_range(min_price, max_price, skip=skip, limit=limit)