from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.base import BaseRepository

class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: Session):
        super().__init__(Product, db)

    def get_by_sku(self, sku: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.sku == sku).first()

    def get_active_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        return self.db.query(Product).filter(Product.is_active == True).offset(skip).limit(limit).all()

    def get_products_by_price_range(self, min_price: float, max_price: float, skip: int = 0, limit: int = 100) -> List[Product]:
        return (self.db.query(Product)
                .filter(Product.price >= min_price, Product.price <= max_price)
                .offset(skip).limit(limit).all())

    def get_products_in_stock(self, skip: int = 0, limit: int = 100) -> List[Product]:
        return (self.db.query(Product)
                .filter(Product.stock_quantity > 0)
                .offset(skip).limit(limit).all())

    def search_products(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Product]:
        return (self.db.query(Product)
                .filter(Product.name.contains(search_term))
                .offset(skip).limit(limit).all())

    def create_product(self, product_data: dict) -> Product:
        return self.create(product_data)

    def update_product(self, product: Product, product_data: dict) -> Product:
        return self.update(product, product_data)