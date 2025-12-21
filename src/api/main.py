from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import health_router, chat_router, ingest_router
from src.api.middleware import LoggingMiddleware, ErrorHandlingMiddleware
from src.core.config import settings
from src.core.logging import setup_logging

def create_app() -> FastAPI:
    setup_logging(settings.log_level)
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if settings.environment == "development" else None,
        redoc_url="/redoc" if settings.environment == "development" else None,
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins if settings.environment == "production" else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)
    
    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(ingest_router)
    
    return app

app = create_app()
