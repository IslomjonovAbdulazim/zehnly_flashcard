from enum import Enum

class ErrorCode(str, Enum):
    # General errors
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    NOT_FOUND = "NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    BAD_REQUEST = "BAD_REQUEST"
    
    # User errors
    USER_NOT_FOUND = "USER_NOT_FOUND"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    USERNAME_ALREADY_EXISTS = "USERNAME_ALREADY_EXISTS"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    WRONG_PASSWORD = "WRONG_PASSWORD"
    INACTIVE_USER = "INACTIVE_USER"
    USER_CREATION_FAILED = "USER_CREATION_FAILED"
    INVALID_EMAIL_FORMAT = "INVALID_EMAIL_FORMAT"
    WEAK_PASSWORD = "WEAK_PASSWORD"
    USERNAME_INVALID = "USERNAME_INVALID"
    
    # Product errors
    PRODUCT_NOT_FOUND = "PRODUCT_NOT_FOUND"
    SKU_ALREADY_EXISTS = "SKU_ALREADY_EXISTS"
    INVALID_PRICE = "INVALID_PRICE"
    INVALID_STOCK_QUANTITY = "INVALID_STOCK_QUANTITY"
    PRODUCT_OUT_OF_STOCK = "PRODUCT_OUT_OF_STOCK"
    PRODUCT_CREATION_FAILED = "PRODUCT_CREATION_FAILED"
    INVALID_SKU_FORMAT = "INVALID_SKU_FORMAT"
    PRODUCT_NAME_INVALID = "PRODUCT_NAME_INVALID"
    
    # Authentication errors
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_MISSING = "TOKEN_MISSING"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Database errors
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_OPERATION_FAILED = "DATABASE_OPERATION_FAILED"
    CONSTRAINT_VIOLATION = "CONSTRAINT_VIOLATION"
    
    # File/Upload errors
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    UPLOAD_FAILED = "UPLOAD_FAILED"
    
    # Business logic errors
    INSUFFICIENT_BALANCE = "INSUFFICIENT_BALANCE"
    OPERATION_NOT_ALLOWED = "OPERATION_NOT_ALLOWED"
    DUPLICATE_OPERATION = "DUPLICATE_OPERATION"
    INVALID_OPERATION_STATE = "INVALID_OPERATION_STATE"
    
    # Vocabulary system errors
    SYSTEM_LIMIT_EXCEEDED = "SYSTEM_LIMIT_EXCEEDED"  # Hard system limits
    PLAN_LIMIT_EXCEEDED = "PLAN_LIMIT_EXCEEDED"      # Plan-specific limits (upgrade needed)

# Error messages for development/logging (not sent to frontend)
ERROR_MESSAGES = {
    ErrorCode.INTERNAL_SERVER_ERROR: "An internal server error occurred",
    ErrorCode.NOT_FOUND: "Resource not found",
    ErrorCode.VALIDATION_ERROR: "Validation failed",
    ErrorCode.UNAUTHORIZED: "Authentication required",
    ErrorCode.FORBIDDEN: "Access forbidden",
    ErrorCode.BAD_REQUEST: "Bad request",
    
    # User errors
    ErrorCode.USER_NOT_FOUND: "User not found",
    ErrorCode.EMAIL_ALREADY_EXISTS: "Email already registered",
    ErrorCode.USERNAME_ALREADY_EXISTS: "Username already taken",
    ErrorCode.INVALID_CREDENTIALS: "Invalid email or password",
    ErrorCode.WRONG_PASSWORD: "Incorrect password",
    ErrorCode.INACTIVE_USER: "User account is inactive",
    ErrorCode.USER_CREATION_FAILED: "Failed to create user",
    ErrorCode.INVALID_EMAIL_FORMAT: "Invalid email format",
    ErrorCode.WEAK_PASSWORD: "Password does not meet requirements",
    ErrorCode.USERNAME_INVALID: "Username contains invalid characters",
    
    # Product errors
    ErrorCode.PRODUCT_NOT_FOUND: "Product not found",
    ErrorCode.SKU_ALREADY_EXISTS: "SKU already exists",
    ErrorCode.INVALID_PRICE: "Invalid price value",
    ErrorCode.INVALID_STOCK_QUANTITY: "Invalid stock quantity",
    ErrorCode.PRODUCT_OUT_OF_STOCK: "Product is out of stock",
    ErrorCode.PRODUCT_CREATION_FAILED: "Failed to create product",
    ErrorCode.INVALID_SKU_FORMAT: "Invalid SKU format",
    ErrorCode.PRODUCT_NAME_INVALID: "Product name is invalid",
    
    # Authentication errors
    ErrorCode.TOKEN_EXPIRED: "Access token has expired",
    ErrorCode.INVALID_TOKEN: "Invalid access token",
    ErrorCode.TOKEN_MISSING: "Access token is missing",
    ErrorCode.INSUFFICIENT_PERMISSIONS: "Insufficient permissions",
    
    # Database errors
    ErrorCode.DATABASE_CONNECTION_ERROR: "Database connection failed",
    ErrorCode.DATABASE_OPERATION_FAILED: "Database operation failed",
    ErrorCode.CONSTRAINT_VIOLATION: "Database constraint violation",
    
    # File/Upload errors
    ErrorCode.FILE_NOT_FOUND: "File not found",
    ErrorCode.INVALID_FILE_TYPE: "Invalid file type",
    ErrorCode.FILE_TOO_LARGE: "File size exceeds limit",
    ErrorCode.UPLOAD_FAILED: "File upload failed",
    
    # Business logic errors
    ErrorCode.INSUFFICIENT_BALANCE: "Insufficient balance",
    ErrorCode.OPERATION_NOT_ALLOWED: "Operation not allowed",
    ErrorCode.DUPLICATE_OPERATION: "Duplicate operation detected",
    ErrorCode.INVALID_OPERATION_STATE: "Invalid operation state",
    
    # Vocabulary system errors
    ErrorCode.SYSTEM_LIMIT_EXCEEDED: "System limit exceeded",
    ErrorCode.PLAN_LIMIT_EXCEEDED: "Plan limit exceeded - upgrade to premium",
}