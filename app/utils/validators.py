from typing import Any, List
from pydantic import validator
import re

class CommonValidators:
    @staticmethod
    def validate_positive_number(v: float) -> float:
        if v <= 0:
            raise ValueError("Value must be positive")
        return v

    @staticmethod
    def validate_non_negative_number(v: float) -> float:
        if v < 0:
            raise ValueError("Value must be non-negative")
        return v

    @staticmethod
    def validate_string_length(v: str, min_length: int = 1, max_length: int = 255) -> str:
        if len(v) < min_length:
            raise ValueError(f"String must be at least {min_length} characters long")
        if len(v) > max_length:
            raise ValueError(f"String must be no more than {max_length} characters long")
        return v

    @staticmethod
    def validate_phone_number(v: str) -> str:
        pattern = r'^\+?1?\d{9,15}$'
        if not re.match(pattern, v):
            raise ValueError("Invalid phone number format")
        return v

    @staticmethod
    def validate_sku(v: str) -> str:
        if not re.match(r'^[A-Z0-9-]{3,20}$', v):
            raise ValueError("SKU must be 3-20 characters long and contain only uppercase letters, numbers, and hyphens")
        return v

    @staticmethod
    def validate_list_not_empty(v: List[Any]) -> List[Any]:
        if not v:
            raise ValueError("List cannot be empty")
        return v

    @staticmethod
    def validate_url(v: str) -> str:
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(v):
            raise ValueError("Invalid URL format")
        return v