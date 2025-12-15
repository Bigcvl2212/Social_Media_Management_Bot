"""
FastAPI Application Entry Point
Main application configuration and middleware setup
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging

from app.core.config import settings
from app.routes import content
from app.routes import instagram

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Social Media Content Manager API",
    description="Complete content creation, editing, and multi-platform posting system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(f"{settings.UPLOAD_DIR}/videos", exist_ok=True)
os.makedirs(f"{settings.UPLOAD_DIR}/images", exist_ok=True)
os.makedirs(f"{settings.UPLOAD_DIR}/audio", exist_ok=True)
os.makedirs(f"{settings.UPLOAD_DIR}/music", exist_ok=True)

# Include routers
app.include_router(content.router)
app.include_router(instagram.router)

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


# ==================== STARTUP/SHUTDOWN EVENTS ====================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("Social Media Content Manager API starting...")
    logger.info(f"Upload directory: {settings.UPLOAD_DIR}")
    logger.info(f"CORS origins: {settings.CORS_ORIGINS}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Social Media Content Manager API shutting down...")


# ==================== ROOT ENDPOINT ====================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Social Media Content Manager API",
        "version": "1.0.0",
        "description": "Complete content creation, editing, and multi-platform posting system",
        "docs": "/api/docs",
        "redoc": "/api/redoc",
        "health_check": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
