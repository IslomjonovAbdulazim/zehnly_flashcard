from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config.settings import settings
from app.core.exceptions import add_exception_handlers

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION + " - Microservice",
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Set up CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Simple middleware to extract user_id from headers
    @app.middleware("http")
    async def add_user_context(request: Request, call_next):
        user_id = request.headers.get("X-User-Id") or request.headers.get("x-user-id")
        request.state.user_id = user_id
        response = await call_next(request)
        return response

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Add exception handlers
    add_exception_handlers(app)

    return app

app = create_application()

@app.get("/")
def root():
    return {"message": "FastAPI Microservice API", "service": "vocabulary-service"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}