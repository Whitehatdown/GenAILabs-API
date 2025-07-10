from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
import time
import logging
from ..models import UploadRequest, UploadResponse
from ..services.embedding import EmbeddingService
from ..services.vector_db import VectorDBService
from ..database import DocumentRepository, ChunkRepository
from ..dependencies import get_vector_db_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.put("/upload", response_model=UploadResponse)
async def upload_documents(
    request: UploadRequest,
    vector_db: VectorDBService = Depends(get_vector_db_service)
):
    """
    Upload document chunks and store them with embeddings.
    
    This endpoint processes journal chunks by:
    1. Validating the input data
    2. Cleaning and preprocessing chunks
    3. Generating embeddings via OpenAI
    4. Storing in ChromaDB and SQLite
    5. Returning processing status
    """
    start_time = time.time()
    processed_chunks = 0
    failed_chunks = 0
    errors = []
    
    try:
        logger.info(f"Starting upload of {len(request.chunks)} chunks")
        
        # Initialize services
        embedding_service = EmbeddingService()
        
        # Process chunks
        valid_chunks = []
        chunk_texts = []
        
        for chunk in request.chunks:
            try:
                # Basic validation and cleaning
                if not chunk.text.strip():
                    errors.append(f"Empty text in chunk {chunk.chunk_id}")
                    failed_chunks += 1
                    continue
                
                # Clean text
                cleaned_text = _clean_chunk_text(chunk.text)
                chunk.text = cleaned_text
                
                valid_chunks.append(chunk)
                chunk_texts.append(cleaned_text)
                
            except Exception as e:
                errors.append(f"Error processing chunk {chunk.chunk_id}: {str(e)}")
                failed_chunks += 1
                continue
        
        if not valid_chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid chunks to process"
            )
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(valid_chunks)} chunks")
        embeddings = await embedding_service.generate_embeddings_batch(chunk_texts)
        
        # Prepare data for storage
        chunks_data = []
        for chunk in valid_chunks:
            chunks_data.append({
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "source_doc_id": chunk.source_doc_id,
                "journal_name": chunk.journal_name,
                "year": chunk.year,
                "section": chunk.section,
                "subsection": chunk.subsection,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index
            })
        
        # Store in ChromaDB
        success = await vector_db.add_documents(chunks_data, embeddings)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store documents in vector database"
            )
        
        # Store metadata in SQLite
        await _store_metadata_in_sqlite(valid_chunks)
        
        processed_chunks = len(valid_chunks)
        processing_time = time.time() - start_time
        
        logger.info(f"Successfully processed {processed_chunks} chunks in {processing_time:.2f}s")
        
        return UploadResponse(
            status="success",
            message=f"Successfully processed {processed_chunks} chunks",
            processed_chunks=processed_chunks,
            failed_chunks=failed_chunks,
            errors=errors,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload processing failed: {str(e)}"
        )

def _clean_chunk_text(text: str) -> str:
    """Clean chunk text for processing."""
    # Remove excessive whitespace
    text = " ".join(text.split())
    
    # Remove problematic characters
    text = text.replace('\x00', '')
    text = text.replace('\ufeff', '')
    
    # Remove extra newlines but preserve paragraph breaks
    text = text.replace('\n\n\n', '\n\n')
    
    return text.strip()

async def _store_metadata_in_sqlite(chunks: List):
    """Store chunk metadata in SQLite database."""
    try:
        # Group chunks by document
        documents = {}
        for chunk in chunks:
            doc_id = chunk.source_doc_id
            if doc_id not in documents:
                documents[doc_id] = {
                    "title": f"{chunk.journal_name} ({chunk.year})",
                    "journal_name": chunk.journal_name,
                    "year": chunk.year,
                    "chunks": []
                }
            documents[doc_id]["chunks"].append(chunk)
        
        # Create document records
        for doc_id, doc_data in documents.items():
            await DocumentRepository.create_document(
                doc_id=doc_id,
                title=doc_data["title"],
                journal_name=doc_data["journal_name"],
                year=doc_data["year"],
                total_chunks=len(doc_data["chunks"])
            )
            
            # Create chunk records
            for chunk in doc_data["chunks"]:
                await ChunkRepository.create_chunk(
                    chunk_id=chunk.chunk_id,
                    source_doc_id=chunk.source_doc_id,
                    chunk_index=chunk.chunk_index,
                    section=chunk.section,
                    subsection=chunk.subsection,
                    page_number=chunk.page_number
                )
        
        logger.info(f"Stored metadata for {len(documents)} documents")
        
    except Exception as e:
        logger.error(f"Failed to store metadata: {e}")
        # Don't raise here as the main operation succeeded
