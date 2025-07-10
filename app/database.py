import aiosqlite
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from .config import settings

logger = logging.getLogger(__name__)

DATABASE_SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    journal_name TEXT NOT NULL,
    year INTEGER NOT NULL,
    total_chunks INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP,
    access_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS chunks (
    chunk_id TEXT PRIMARY KEY,
    source_doc_id TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    section TEXT,
    subsection TEXT,
    page_number INTEGER,
    usage_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP,
    FOREIGN KEY (source_doc_id) REFERENCES documents (id)
);

CREATE TABLE IF NOT EXISTS search_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    results_count INTEGER NOT NULL,
    search_time REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_documents_journal_year ON documents (journal_name, year);
CREATE INDEX IF NOT EXISTS idx_chunks_source_doc ON chunks (source_doc_id);
CREATE INDEX IF NOT EXISTS idx_chunks_usage ON chunks (usage_count DESC);
"""

async def init_db():
    """Initialize the SQLite database with required tables."""
    try:
        async with aiosqlite.connect(settings.sqlite_database_path) as db:
            await db.executescript(DATABASE_SCHEMA)
            await db.commit()
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def get_db():
    """Get database connection."""
    async with aiosqlite.connect(settings.sqlite_database_path) as db:
        db.row_factory = aiosqlite.Row
        yield db

class DocumentRepository:
    """Repository for document operations."""
    
    @staticmethod
    async def create_document(doc_id: str, title: str, journal_name: str, 
                            year: int, total_chunks: int) -> bool:
        """Create a new document record."""
        try:
            async with aiosqlite.connect(settings.sqlite_database_path) as db:
                await db.execute(
                    """INSERT OR REPLACE INTO documents 
                       (id, title, journal_name, year, total_chunks) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (doc_id, title, journal_name, year, total_chunks)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            return False
    
    @staticmethod
    async def get_document(doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        try:
            async with aiosqlite.connect(settings.sqlite_database_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    "SELECT * FROM documents WHERE id = ?", (doc_id,)
                )
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get document: {e}")
            return None
    
    @staticmethod
    async def update_document_access(doc_id: str) -> bool:
        """Update document access timestamp and count."""
        try:
            async with aiosqlite.connect(settings.sqlite_database_path) as db:
                await db.execute(
                    """UPDATE documents 
                       SET last_accessed = CURRENT_TIMESTAMP, 
                           access_count = access_count + 1 
                       WHERE id = ?""",
                    (doc_id,)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to update document access: {e}")
            return False

class ChunkRepository:
    """Repository for chunk operations."""
    
    @staticmethod
    async def create_chunk(chunk_id: str, source_doc_id: str, chunk_index: int,
                          section: Optional[str] = None, subsection: Optional[str] = None,
                          page_number: Optional[int] = None) -> bool:
        """Create a new chunk record."""
        try:
            async with aiosqlite.connect(settings.sqlite_database_path) as db:
                await db.execute(
                    """INSERT OR REPLACE INTO chunks 
                       (chunk_id, source_doc_id, chunk_index, section, subsection, page_number) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (chunk_id, source_doc_id, chunk_index, section, subsection, page_number)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to create chunk: {e}")
            return False
    
    @staticmethod
    async def update_chunk_usage(chunk_ids: List[str]) -> bool:
        """Update usage count for multiple chunks."""
        try:
            async with aiosqlite.connect(settings.sqlite_database_path) as db:
                placeholders = ",".join(["?" for _ in chunk_ids])
                await db.execute(
                    f"""UPDATE chunks 
                        SET usage_count = usage_count + 1, 
                            last_accessed = CURRENT_TIMESTAMP 
                        WHERE chunk_id IN ({placeholders})""",
                    chunk_ids
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to update chunk usage: {e}")
            return False
    
    @staticmethod
    async def get_chunks_for_document(doc_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a document."""
        try:
            async with aiosqlite.connect(settings.sqlite_database_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    """SELECT * FROM chunks 
                       WHERE source_doc_id = ? 
                       ORDER BY chunk_index""",
                    (doc_id,)
                )
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get chunks for document: {e}")
            return []

class SearchLogRepository:
    """Repository for search log operations."""
    
    @staticmethod
    async def log_search(query: str, results_count: int, search_time: float) -> bool:
        """Log a search query."""
        try:
            async with aiosqlite.connect(settings.sqlite_database_path) as db:
                await db.execute(
                    """INSERT INTO search_logs (query, results_count, search_time) 
                       VALUES (?, ?, ?)""",
                    (query, results_count, search_time)
                )
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to log search: {e}")
            return False
