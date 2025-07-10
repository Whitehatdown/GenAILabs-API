"""
Dependencies for FastAPI dependency injection.
"""
from .services.vector_db import VectorDBService

# Global services
vector_db_service = None

def get_vector_db_service() -> VectorDBService:
    """Get the vector database service instance."""
    return vector_db_service

def set_vector_db_service(service: VectorDBService):
    """Set the vector database service instance."""
    global vector_db_service
    vector_db_service = service
