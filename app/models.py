from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

class ChunkData(BaseModel):
    chunk_id: str = Field(..., description="Unique identifier for the chunk")
    text: str = Field(..., description="The actual text content of the chunk")
    chunk_index: int = Field(..., description="Order of this chunk in the document")
    source_doc_id: str = Field(..., description="Identifier of the source document")
    journal_name: str = Field(..., description="Name of the journal")
    year: int = Field(..., description="Publication year")
    section: Optional[str] = Field(None, description="Section of the document")
    subsection: Optional[str] = Field(None, description="Subsection of the document")
    page_number: Optional[int] = Field(None, description="Page number in the document")
    
    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Text content cannot be empty')
        return v.strip()
    
    @validator('year')
    def year_must_be_reasonable(cls, v):
        current_year = datetime.now().year
        if v < 1900 or v > current_year + 1:
            raise ValueError(f'Year must be between 1900 and {current_year + 1}')
        return v

class UploadRequest(BaseModel):
    schema_version: str = Field("1.0", description="Version of the schema")
    chunks: List[ChunkData] = Field(..., description="List of document chunks to upload")
    
    @validator('chunks')
    def chunks_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Chunks list cannot be empty')
        return v

class UploadResponse(BaseModel):
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Human-readable message")
    processed_chunks: int = Field(..., description="Number of chunks successfully processed")
    failed_chunks: int = Field(0, description="Number of chunks that failed processing")
    errors: List[str] = Field(default_factory=list, description="List of error messages")
    processing_time: float = Field(..., description="Time taken to process in seconds")

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query text")
    k: int = Field(10, description="Number of results to return")
    min_score: Optional[float] = Field(0.7, description="Minimum similarity score")
    journal_filter: Optional[str] = Field(None, description="Filter by journal name")
    year_filter: Optional[int] = Field(None, description="Filter by publication year")
    generate_answer: bool = Field(False, description="Whether to generate an AI answer")
    
    @validator('query')
    def query_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()
    
    @validator('k')
    def k_must_be_reasonable(cls, v):
        if v < 1 or v > 50:
            raise ValueError('k must be between 1 and 50')
        return v

class SearchResult(BaseModel):
    chunk_id: str
    text: str
    similarity_score: float
    source_doc_id: str
    journal_name: str
    year: int
    section: Optional[str]
    subsection: Optional[str]
    page_number: Optional[int]
    usage_count: int

class GeneratedAnswer(BaseModel):
    answer: str
    citations: List[str]
    confidence: float

class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    total_results: int
    search_time: float
    generated_answer: Optional[GeneratedAnswer] = None

class JournalStats(BaseModel):
    total_chunks: int
    sections: Dict[str, int]
    most_popular_section: Optional[str]
    total_views: int
    last_accessed: Optional[datetime]
    average_chunk_length: float

class JournalResponse(BaseModel):
    journal_id: str
    title: str
    journal_name: str
    year: int
    chunks: List[SearchResult]
    stats: JournalStats
    related_documents: List[str]
    
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
