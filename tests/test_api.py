import pytest
import asyncio
from httpx import AsyncClient
from app.main import app

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

class TestUploadAPI:
    """Test cases for the upload API."""
    
    async def test_upload_valid_chunks(self, client: AsyncClient):
        """Test uploading valid chunks."""
        test_data = {
            "schema_version": "1.0",
            "chunks": [
                {
                    "chunk_id": "test_chunk_1",
                    "text": "This is a test chunk about mucuna pruriens benefits.",
                    "chunk_index": 0,
                    "source_doc_id": "test_doc_1",
                    "journal_name": "Test Journal",
                    "year": 2023,
                    "section": "Introduction"
                }
            ]
        }
        
        response = await client.put("/api/upload", json=test_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["status"] == "success"
        assert result["processed_chunks"] == 1
        assert result["failed_chunks"] == 0
    
    async def test_upload_invalid_chunks(self, client: AsyncClient):
        """Test uploading invalid chunks."""
        test_data = {
            "schema_version": "1.0",
            "chunks": [
                {
                    "chunk_id": "test_chunk_2",
                    "text": "",  # Empty text should fail
                    "chunk_index": 0,
                    "source_doc_id": "test_doc_2",
                    "journal_name": "Test Journal",
                    "year": 2023
                }
            ]
        }
        
        response = await client.put("/api/upload", json=test_data)
        assert response.status_code == 422  # Validation error

class TestSearchAPI:
    """Test cases for the search API."""
    
    async def test_similarity_search(self, client: AsyncClient):
        """Test similarity search."""
        test_data = {
            "query": "mucuna pruriens benefits",
            "k": 5,
            "generate_answer": False
        }
        
        response = await client.post("/api/similarity_search", json=test_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "results" in result
        assert "query" in result
        assert "search_time" in result
    
    async def test_search_with_answer_generation(self, client: AsyncClient):
        """Test search with answer generation."""
        test_data = {
            "query": "What are the benefits of mucuna pruriens?",
            "k": 3,
            "generate_answer": True
        }
        
        response = await client.post("/api/similarity_search", json=test_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "results" in result
        # Note: generated_answer might be None if no results found

class TestJournalAPI:
    """Test cases for the journal API."""
    
    async def test_get_nonexistent_journal(self, client: AsyncClient):
        """Test getting a journal that doesn't exist."""
        response = await client.get("/api/nonexistent_journal")
        assert response.status_code == 404

class TestHealthCheck:
    """Test cases for health check endpoints."""
    
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint."""
        response = await client.get("/")
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "version" in result
    
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        
        result = response.json()
        assert result["status"] == "healthy"
