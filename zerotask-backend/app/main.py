from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.config import settings
from app.database import create_tables
from app.api import health, auth, gmail

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    print("Starting ZeroTask API...")
    print(f"Database: {settings.database_url}")
    print(f"LLM: {settings.ollama_base_url}/{settings.ollama_model}")
    
    # Create database tables
    create_tables()
    print("Database tables created/verified")
    
    # TODO: Start background job scheduler
    print("Background jobs initialized")
    
    yield
    
    # Shutdown
    print("Shutting down ZeroTask API...")
    # TODO: Shutdown background job scheduler

# Create FastAPI application with lifespan
app = FastAPI(
    title="ZeroTask API",
    description="Local-first daily brief system for Gmail, Slack & GitHub",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(gmail.router, prefix="/api/v1/gmail")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ZeroTask API - Local-first daily brief system",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs" if settings.debug else None
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )