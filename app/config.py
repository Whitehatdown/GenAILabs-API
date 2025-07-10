from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Groq Configuration
    groq_api_key: str
    embedding_model: str = "text-embedding-3-small"  # Note: We'll use a different service for embeddings
    llm_model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    
    # Database Configuration
    chroma_persist_directory: str = "./chroma_db"
    sqlite_database_path: str = "./app.db"
    
    # API Configuration
    log_level: str = "INFO"
    batch_size: int = 100
    max_retries: int = 3
    
    # Search Configuration
    default_k: int = 10
    max_k: int = 50
    min_similarity_score: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
