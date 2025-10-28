from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.error_codes import ErrorCode, ERROR_MESSAGES

class APIException(HTTPException):
    def __init__(
        self, 
        status_code: int, 
        error_code: ErrorCode, 
        detail: str = None, 
        headers: dict = None
    ):
        self.error_code = error_code
        super().__init__(status_code, detail or ERROR_MESSAGES.get(error_code, "Unknown error"), headers)

def add_exception_handlers(app: FastAPI):
    
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "message": exc.detail
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        error_code_map = {
            404: ErrorCode.NOT_FOUND,
            401: ErrorCode.UNAUTHORIZED,
            403: ErrorCode.FORBIDDEN,
            400: ErrorCode.BAD_REQUEST,
        }
        
        error_code = error_code_map.get(exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR)
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": error_code,
                "message": exc.detail
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error_code": ErrorCode.VALIDATION_ERROR,
                "message": "Validation failed",
                "details": exc.errors()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error_code": ErrorCode.INTERNAL_SERVER_ERROR,
                "message": "Internal server error"
            }
        )