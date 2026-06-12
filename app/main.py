"""Main application module."""

import logging
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .api.api import api_router
from .core.logger import setup_logging
from .core.config import settings
from .repositories.database import get_session, database
from .repositories.task_repository import TaskRepository
from .core.redis import redis_client

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


@app.on_event("startup")
async def startup():
    """Startup event handler."""
    await database.connect()
    # Initialize Redis client
    try:
        logger = logging.getLogger(__name__)
        logger.info("Connecting to Redis at %s:%s", settings.REDIS_HOST, settings.REDIS_PORT)
        await redis_client.get_client()
        logger.info("Redis client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Redis client: {e}")


@app.on_event("shutdown")
async def shutdown():
    """Shutdown event handler."""
    await database.disconnect()
    await redis_client.close()


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": settings.APP_NAME}


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    logger = logging.getLogger(__name__)
    db_healthy = await database.health_check()
    redis_healthy = await redis_client.health_check()
    
    logger.info("Readiness check: DB=%s, Redis=%s", db_healthy, redis_healthy)
    
    if not db_healthy or not redis_healthy:
        return {
            "status": "not_ready", 
            "database": "healthy" if db_healthy else "unhealthy",
            "redis": "healthy" if redis_healthy else "unhealthy"
        }
    
    return {
        "status": "ready", 
        "database": "healthy",
        "redis": "healthy"
    }
