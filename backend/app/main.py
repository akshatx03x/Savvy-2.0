from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.database import init_db
from app.api.v1.router import api_router

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing LeadSynth AI Backend Server...")
    await init_db()
    logger.info(f"Database initialized. Environment: {settings.ENVIRONMENT}. Synthetic Data Enabled: {settings.ENABLE_SYNTHETIC_DATA}")
    yield
    logger.info("Shutting down LeadSynth AI Backend Server...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "synthetic_data_enabled": settings.ENABLE_SYNTHETIC_DATA,
    }
