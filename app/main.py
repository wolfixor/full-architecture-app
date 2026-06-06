"""Main application module."""

from fastapi import FastAPI
from .api.api import api_router
from .core.logger import setup_logging
from .core.config import settings


# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include API router
app.include_router(api_router, prefix="/api")

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "task-api-new-version"}