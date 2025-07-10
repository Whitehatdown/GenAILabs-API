from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict, Any
import time
import logging
from ..models import SearchRequest, SearchResponse, SearchResult, GeneratedAnswer
from ..services.embedding import EmbeddingService
from ..services.vector_db import VectorDBService
from ..services.llm import LLMService
from ..database import ChunkRepository, SearchLogRepository
from ..dependencies import get_vector_db_service
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/similarity_search", response_model=SearchResponse)
async def similarity_search(
    request: SearchRequest,
    vector_db: VectorDBService = Depends(get_vector_db_service)
):
    """
    Perform similarity search on document chunks.
    
    This endpoint:
    1. Validates the search query
    2. Generates query embedding
    3. Searches ChromaDB for similar chunks
    4. Updates usage statistics
    5. Optionally generates AI answer
    6. Returns results with metadata
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting similarity search for query: {request.query[:50]}...")
        
        # Initialize services
        embedding_service = EmbeddingService()
        
        # Generate query embedding
        query_embeddings = await embedding_service.generate_embeddings([request.query])
        query_embedding = query_embeddings[0]
        
        # Build filters
        filters = {}
        if request.journal_filter:
            filters["journal_name"] = request.journal_filter
        if request.year_filter:
            filters["year"] = request.year_filter
        
        # Search ChromaDB
        raw_results = await vector_db.search_similar(
            query_embedding=query_embedding,
            k=request.k,
            filters=filters if filters else None
        )
        
        # Filter by minimum score
        filtered_results = [
            result for result in raw_results
            if result["similarity_score"] >= request.min_score
        ]
        
        # Convert to SearchResult format
        search_results = []
        chunk_ids = []
        
        for result in filtered_results:
            metadata = result["metadata"]
            search_result = SearchResult(
                chunk_id=result["chunk_id"],
                text=result["text"],
                similarity_score=result["similarity_score"],
                source_doc_id=metadata.get("source_doc_id", ""),
                journal_name=metadata.get("journal_name", ""),
                year=metadata.get("year", 0),
                section=metadata.get("section"),
                subsection=metadata.get("subsection"),
                page_number=metadata.get("page_number"),
                usage_count=metadata.get("usage_count", 0)
            )
            search_results.append(search_result)
            chunk_ids.append(result["chunk_id"])
        
        # Update usage statistics
        if chunk_ids:
            await ChunkRepository.update_chunk_usage(chunk_ids)
        
        # Generate AI answer if requested
        generated_answer = None
        if request.generate_answer and search_results:
            try:
                llm_service = LLMService()
                answer_data = await llm_service.generate_answer(
                    query=request.query,
                    context_chunks=filtered_results
                )
                generated_answer = GeneratedAnswer(
                    answer=answer_data["answer"],
                    citations=answer_data["citations"],
                    confidence=answer_data["confidence"]
                )
            except Exception as e:
                logger.warning(f"Failed to generate answer: {e}")
                # Continue without answer rather than failing the whole request
        
        search_time = time.time() - start_time
        
        # Log the search
        await SearchLogRepository.log_search(
            query=request.query,
            results_count=len(search_results),
            search_time=search_time
        )
        
        logger.info(f"Search completed: {len(search_results)} results in {search_time:.2f}s")
        
        return SearchResponse(
            results=search_results,
            query=request.query,
            total_results=len(search_results),
            search_time=search_time,
            generated_answer=generated_answer
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search processing failed: {str(e)}"
        )

@router.get("/search_stats")
async def get_search_stats():
    """Get search statistics and popular queries."""
    try:
        # This would be implemented to return search analytics
        # For now, return basic stats
        return {
            "message": "Search stats endpoint - to be implemented",
            "total_searches": 0,
            "popular_queries": []
        }
    except Exception as e:
        logger.error(f"Failed to get search stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve search statistics"
        )
