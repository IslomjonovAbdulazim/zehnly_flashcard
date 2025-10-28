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

    # Middleware to extract user_id from headers
    @app.middleware("http")
    async def add_user_context(request: Request, call_next):
        # Extract user_id from header sent by main server
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
async def root():
    return {"message": "FastAPI Microservice API", "service": "user-service"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "user-service"}