from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict, Any
import logging
from ..models import JournalResponse, JournalStats, SearchResult
from ..services.vector_db import VectorDBService
from ..database import DocumentRepository, ChunkRepository
from ..dependencies import get_vector_db_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{journal_id}", response_model=JournalResponse)
async def get_journal(
    journal_id: str,
    vector_db: VectorDBService = Depends(get_vector_db_service)
):
    """
    Get all information about a specific journal document.
    
    This endpoint:
    1. Validates journal exists
    2. Retrieves all chunks for the journal
    3. Calculates usage statistics
    4. Updates access tracking
    5. Returns complete journal information
    """
    try:
        logger.info(f"Retrieving journal: {journal_id}")
        
        # Check if document exists
        document = await DocumentRepository.get_document(journal_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Journal with ID '{journal_id}' not found"
            )
        
        # Get all chunks for this document from ChromaDB
        chunks_data = await vector_db.get_documents_by_source(journal_id)
        
        if not chunks_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No chunks found for journal '{journal_id}'"
            )
        
        # Get chunk metadata from SQLite
        sqlite_chunks = await ChunkRepository.get_chunks_for_document(journal_id)
        chunk_metadata = {chunk["chunk_id"]: chunk for chunk in sqlite_chunks}
        
        # Convert to SearchResult format
        search_results = []
        sections = {}
        total_usage = 0
        total_text_length = 0
        
        for chunk in chunks_data:
            metadata = chunk["metadata"]
            chunk_id = chunk["chunk_id"]
            
            # Get additional metadata from SQLite
            sqlite_metadata = chunk_metadata.get(chunk_id, {})
            
            # Track sections
            section = metadata.get("section", "Unknown")
            if section not in sections:
                sections[section] = 0
            sections[section] += 1
            
            # Track usage
            usage_count = sqlite_metadata.get("usage_count", 0)
            total_usage += usage_count
            total_text_length += len(chunk["text"])
            
            search_result = SearchResult(
                chunk_id=chunk_id,
                text=chunk["text"],
                similarity_score=1.0,  # Not applicable for direct retrieval
                source_doc_id=metadata.get("source_doc_id", ""),
                journal_name=metadata.get("journal_name", ""),
                year=metadata.get("year", 0),
                section=metadata.get("section"),
                subsection=metadata.get("subsection"),
                page_number=metadata.get("page_number"),
                usage_count=usage_count
            )
            search_results.append(search_result)
        
        # Calculate statistics
        most_popular_section = max(sections.keys(), key=lambda k: sections[k]) if sections else None
        average_chunk_length = total_text_length / len(chunks_data) if chunks_data else 0
        
        stats = JournalStats(
            total_chunks=len(chunks_data),
            sections=sections,
            most_popular_section=most_popular_section,
            total_views=total_usage,
            last_accessed=document.get("last_accessed"),
            average_chunk_length=average_chunk_length
        )
        
        # Find related documents (simplified implementation)
        related_documents = await _find_related_documents(journal_id, document["journal_name"])
        
        # Update access tracking
        await DocumentRepository.update_document_access(journal_id)
        
        logger.info(f"Successfully retrieved journal {journal_id} with {len(search_results)} chunks")
        
        return JournalResponse(
            journal_id=journal_id,
            title=document["title"],
            journal_name=document["journal_name"],
            year=document["year"],
            chunks=search_results,
            stats=stats,
            related_documents=related_documents
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve journal {journal_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve journal: {str(e)}"
        )

async def _find_related_documents(journal_id: str, journal_name: str) -> List[str]:
    """Find documents related to the current journal."""
    try:
        # Simple implementation: find documents from the same journal
        # In a more sophisticated implementation, you could use embeddings
        # to find semantically similar documents
        
        # This is a placeholder - you'd implement actual similarity search
        related = []
        
        # For now, just return empty list
        # TODO: Implement semantic similarity search for related documents
        
        return related
        
    except Exception as e:
        logger.error(f"Failed to find related documents: {e}")
        return []

@router.get("/{journal_id}/stats")
async def get_journal_stats(journal_id: str):
    """Get detailed statistics for a journal."""
    try:
        document = await DocumentRepository.get_document(journal_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Journal with ID '{journal_id}' not found"
            )
        
        # Get chunk statistics
        chunks = await ChunkRepository.get_chunks_for_document(journal_id)
        
        stats = {
            "document_id": journal_id,
            "title": document["title"],
            "total_chunks": len(chunks),
            "total_access_count": document.get("access_count", 0),
            "created_at": document.get("created_at"),
            "last_accessed": document.get("last_accessed"),
            "chunk_usage": [
                {
                    "chunk_id": chunk["chunk_id"],
                    "usage_count": chunk.get("usage_count", 0),
                    "last_accessed": chunk.get("last_accessed")
                }
                for chunk in chunks
            ]
        }
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get journal stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve journal statistics"
        )
