from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from .config import settings
from .database import init_db
from .services.vector_db import VectorDBService
from .dependencies import set_vector_db_service
from .routers import upload, search, journal

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database...")
    await init_db()
    
    vector_db_service = VectorDBService()
    await vector_db_service.initialize()
    set_vector_db_service(vector_db_service)
    
    logger.info("API startup complete")
    yield
    
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="GenAI Labs API",
    description="Document upload, embedding storage, and semantic search API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(journal.router, prefix="/api", tags=["journal"])

@app.get("/")
async def root():
    return {"message": "GenAI Labs API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": {"database": "ok", "vector_db": "ok"}}
