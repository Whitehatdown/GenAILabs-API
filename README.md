# FastAPI GenAI Labs API

A FastAPI-based API for document upload, embedding generation, and semantic search using ChromaDB and OpenAI.

## Features

- **Document Upload**: Upload journal chunks with automatic embedding generation
- **Semantic Search**: Search documents using natural language queries
- **AI-Generated Answers**: Get comprehensive answers with citations
- **Journal Management**: Retrieve complete journal information and statistics
- **Usage Analytics**: Track document and chunk usage patterns

## Project Structure

```
GenAILabs-API/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app and configuration
│   ├── config.py            # Settings and configuration
│   ├── models.py            # Pydantic models
│   ├── database.py          # SQLite database operations
│   ├── routers/             # API route handlers
│   │   ├── __init__.py
│   │   ├── upload.py        # Document upload endpoints
│   │   ├── search.py        # Search endpoints
│   │   └── journal.py       # Journal retrieval endpoints
│   └── services/            # Business logic services
│       ├── __init__.py
│       ├── embedding.py     # OpenAI embedding service
│       ├── vector_db.py     # ChromaDB operations
│       └── llm.py           # OpenAI LLM service
├── tests/
│   ├── __init__.py
│   └── test_api.py          # API tests
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── run.py                  # Application entry point
└── README.md               # This file
```

## Setup Instructions

### 1. Environment Setup

Create a virtual environment and install dependencies:

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On macOS/Linux

pip install -r requirements.txt
```

### 2. Environment Variables

Copy `.env.example` to `.env` and fill in your configuration:

```bash
cp .env.example .env
```

Edit `.env` with your settings:
```
OPENAI_API_KEY=your_openai_api_key_here
CHROMA_PERSIST_DIRECTORY=./chroma_db
SQLITE_DATABASE_PATH=./app.db
LOG_LEVEL=INFO
```

### 3. Run the Application

```bash
python run.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Upload Documents
```
PUT /api/upload
```
Upload document chunks with automatic embedding generation.

### Search Documents
```
POST /api/similarity_search
```
Search for similar documents using natural language queries.

### Get Journal Information
```
GET /api/{journal_id}
```
Retrieve complete information about a specific journal.

### Health Check
```
GET /health
```
Check API health status.

## API Documentation

Once running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Testing

Run tests with pytest:

```bash
pytest tests/
```

## Usage Examples

### Upload Documents

```python
import requests

data = {
    "schema_version": "1.0",
    "chunks": [
        {
            "chunk_id": "chunk_1",
            "text": "Mucuna pruriens is a tropical legume...",
            "chunk_index": 0,
            "source_doc_id": "doc_123",
            "journal_name": "Journal of Ethnopharmacology",
            "year": 2023,
            "section": "Introduction"
        }
    ]
}

response = requests.put("http://localhost:8000/api/upload", json=data)
print(response.json())
```

### Search Documents

```python
import requests

search_data = {
    "query": "What are the benefits of mucuna pruriens?",
    "k": 5,
    "generate_answer": True
}

response = requests.post("http://localhost:8000/api/similarity_search", json=search_data)
results = response.json()
```

## Architecture

The API follows a clean architecture pattern:

1. **Routers**: Handle HTTP requests and responses
2. **Services**: Business logic and external API interactions
3. **Database**: Data persistence with SQLite for metadata and ChromaDB for vectors
4. **Models**: Pydantic models for request/response validation

## Dependencies

- **FastAPI**: Web framework
- **ChromaDB**: Vector database for embeddings
- **OpenAI**: Embedding and LLM services
- **SQLite**: Metadata storage
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

## Error Handling

The API implements comprehensive error handling:
- Validation errors return 422 with detailed messages
- External service failures return 503 with retry suggestions
- Database errors return 500 with generic messages
- Not found errors return 404 with helpful information

## Production Considerations

Before deploying to production:

1. Configure CORS origins properly
2. Set up proper logging and monitoring
3. Implement rate limiting
4. Add authentication and authorization
5. Use environment-specific configurations
6. Set up database backups
7. Configure SSL/TLS

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Run the test suite
5. Submit a pull request

## License

This project is licensed under the MIT License.
This is a RAG based Application which has ingestion pipeline for the documents and information. Later post processing and has advanced features like summary and AI Data Fetch. 
