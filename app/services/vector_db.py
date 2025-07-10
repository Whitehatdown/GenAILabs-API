from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
import logging
from ..config import settings

logger = logging.getLogger(__name__)

class VectorDBService:
    """Service for managing ChromaDB operations."""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.collection_name = "document_chunks"
    
    async def initialize(self):
        """Initialize ChromaDB client and collection."""
        try:
            # Create persistent client
            self.client = chromadb.PersistentClient(
                path=settings.chroma_persist_directory,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"ChromaDB initialized with collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    async def add_documents(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> bool:
        """Add documents with embeddings to ChromaDB."""
        try:
            # Prepare data for ChromaDB
            ids = [chunk["chunk_id"] for chunk in chunks]
            documents = [chunk["text"] for chunk in chunks]
            metadatas = [
                {
                    "source_doc_id": chunk["source_doc_id"],
                    "journal_name": chunk["journal_name"],
                    "year": chunk["year"],
                    "section": chunk.get("section", ""),
                    "subsection": chunk.get("subsection", ""),
                    "page_number": chunk.get("page_number", 0),
                    "chunk_index": chunk["chunk_index"],
                    "usage_count": 0
                }
                for chunk in chunks
            ]
            
            # Add to collection
            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(chunks)} documents to ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to ChromaDB: {e}")
            return False
    
    async def search_similar(self, query_embedding: List[float], k: int = 10,
                           filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar documents in ChromaDB."""
        try:
            # Build where clause for filtering
            where_clause = {}
            if filters:
                if "journal_name" in filters:
                    where_clause["journal_name"] = filters["journal_name"]
                if "year" in filters:
                    where_clause["year"] = filters["year"]
            
            # Perform search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=where_clause if where_clause else None
            )
            
            # Format results
            formatted_results = []
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    result = {
                        "chunk_id": results["ids"][0][i],
                        "text": results["documents"][0][i],
                        "similarity_score": 1 - results["distances"][0][i],  # Convert distance to similarity
                        "metadata": results["metadatas"][0][i]
                    }
                    formatted_results.append(result)
            
            logger.info(f"Found {len(formatted_results)} similar documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search ChromaDB: {e}")
            return []
    
    async def get_documents_by_source(self, source_doc_id: str) -> List[Dict[str, Any]]:
        """Get all documents for a specific source document."""
        try:
            results = self.collection.get(
                where={"source_doc_id": source_doc_id}
            )
            
            formatted_results = []
            if results["ids"]:
                for i in range(len(results["ids"])):
                    result = {
                        "chunk_id": results["ids"][i],
                        "text": results["documents"][i],
                        "metadata": results["metadatas"][i]
                    }
                    formatted_results.append(result)
            
            # Sort by chunk_index
            formatted_results.sort(key=lambda x: x["metadata"].get("chunk_index", 0))
            
            logger.info(f"Retrieved {len(formatted_results)} documents for source: {source_doc_id}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to get documents by source: {e}")
            return []
    
    async def update_usage_count(self, chunk_ids: List[str]) -> bool:
        """Update usage count for chunks."""
        try:
            # ChromaDB doesn't support direct metadata updates, so we'll handle this in SQLite
            # This is a placeholder for consistency
            return True
            
        except Exception as e:
            logger.error(f"Failed to update usage count: {e}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection_name
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"total_documents": 0, "collection_name": self.collection_name}
