import re
from typing import Optional
from datetime import datetime

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"

def generate_sku(product_name: str, category: str = "") -> str:
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', product_name.upper())[:6]
    clean_category = re.sub(r'[^a-zA-Z0-9]', '', category.upper())[:3]
    timestamp = datetime.now().strftime("%m%d")
    
    if clean_category:
        return f"{clean_category}-{clean_name}-{timestamp}"
    return f"{clean_name}-{timestamp}"

def format_currency(amount: float, currency: str = "USD") -> str:
    return f"{currency} {amount:.2f}"

def calculate_discount_price(original_price: float, discount_percentage: float) -> float:
    if discount_percentage < 0 or discount_percentage > 100:
        raise ValueError("Discount percentage must be between 0 and 100")
    
    discount_amount = original_price * (discount_percentage / 100)
    return round(original_price - discount_amount, 2)

def sanitize_filename(filename: str) -> str:
    return re.sub(r'[^\w\s-]', '', filename).strip()

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix