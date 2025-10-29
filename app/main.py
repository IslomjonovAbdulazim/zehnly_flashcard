import time
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

    # Performance timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        
        # Extract user_id from header sent by main server
        user_id = request.headers.get("X-User-Id") or request.headers.get("x-user-id")
        request.state.user_id = user_id
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log slow requests
        if process_time > 1.0:  # Log requests taking more than 1 second
            print(f"🐌 SLOW REQUEST: {request.method} {request.url} took {process_time:.3f}s")
        
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
def health_check():
    return {"status": "healthy", "service": "vocabulary-service", "timestamp": time.time()}

@app.get("/health/db")
def health_check_db():
    """Database health check to warm up connections"""
    from app.config.database import engine
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1").fetchone()
            return {"status": "healthy", "database": "connected", "result": result[0]}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}