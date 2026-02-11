"""FastAPI application setup"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from prometheus_client import make_asgi_app

from ..core.config import get_settings, Settings
from .routes import chat, completion, code, rag, multimodal, health


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting GenAI Platform API")
    yield
    logger.info("Shutting down GenAI Platform API")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Production-ready, cloud-agnostic Generative AI platform",
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health.router, prefix=settings.api_prefix, tags=["health"])
    app.include_router(chat.router, prefix=settings.api_prefix, tags=["chat"])
    app.include_router(completion.router, prefix=settings.api_prefix, tags=["completion"])
    app.include_router(code.router, prefix=settings.api_prefix, tags=["code"])
    app.include_router(rag.router, prefix=settings.api_prefix, tags=["rag"])
    app.include_router(multimodal.router, prefix=settings.api_prefix, tags=["multimodal"])
    
    # Prometheus metrics
    if settings.enable_prometheus:
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)
    
    return app


app = create_app()
