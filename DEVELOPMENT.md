# Development Guide - GenAI Labs API

## Quick Start

1. **Set up the environment:**
   ```bash
   python setup.py
   ```

2. **Configure your environment:**
   - Edit `.env` file with your OpenAI API key
   - Adjust other settings as needed

3. **Start the API:**
   ```bash
   python run.py
   ```

4. **Test the setup:**
   ```bash
   python test_setup.py
   ```

## Step-by-Step Development Process

### Phase 1: Basic Setup ✅
- [x] Project structure created
- [x] Dependencies defined
- [x] Basic FastAPI app
- [x] Configuration management
- [x] Database schemas

### Phase 2: Core Services ✅
- [x] OpenAI embedding service
- [x] ChromaDB vector database service
- [x] OpenAI LLM service
- [x] SQLite database operations

### Phase 3: API Endpoints ✅
- [x] Upload endpoint (`PUT /api/upload`)
- [x] Search endpoint (`POST /api/similarity_search`)
- [x] Journal endpoint (`GET /api/{journal_id}`)
- [x] Health check endpoints

### Phase 4: Testing & Validation ✅
- [x] Basic test suite
- [x] Setup verification script
- [x] API integration tests

## Next Development Steps

### Phase 5: Production Readiness
- [ ] Add comprehensive logging
- [ ] Implement rate limiting
- [ ] Add authentication/authorization
- [ ] Error handling improvements
- [ ] Database connection pooling
- [ ] Docker containerization

### Phase 6: Advanced Features
- [ ] Batch processing endpoints
- [ ] Advanced search filters
- [ ] Document similarity analysis
- [ ] Usage analytics dashboard
- [ ] Export/import functionality

### Phase 7: Performance Optimization
- [ ] Async processing for large uploads
- [ ] Caching layer
- [ ] Database indexing optimization
- [ ] Embedding caching
- [ ] Load balancing considerations

## API Usage Examples

### 1. Upload Documents

```python
import requests
import json

# Sample document chunks
data = {
    "schema_version": "1.0",
    "chunks": [
        {
            "chunk_id": "mucuna_intro_1",
            "text": "Mucuna pruriens, commonly known as velvet bean, is a tropical legume native to Africa and tropical Asia. It has been used in traditional medicine for centuries and is now gaining attention in modern research for its potential therapeutic benefits.",
            "chunk_index": 0,
            "source_doc_id": "mucuna_review_2023",
            "journal_name": "Journal of Ethnopharmacology",
            "year": 2023,
            "section": "Introduction",
            "page_number": 1
        },
        {
            "chunk_id": "mucuna_benefits_1",
            "text": "Studies have shown that Mucuna pruriens seeds contain high levels of L-DOPA, a precursor to dopamine. This makes it potentially beneficial for treating Parkinson's disease and other neurological conditions. The plant also contains other bioactive compounds that may contribute to its therapeutic effects.",
            "chunk_index": 1,
            "source_doc_id": "mucuna_review_2023",
            "journal_name": "Journal of Ethnopharmacology",
            "year": 2023,
            "section": "Bioactive Compounds",
            "page_number": 2
        }
    ]
}

response = requests.put("http://localhost:8000/api/upload", json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

### 2. Search Documents

```python
import requests

# Basic search
search_data = {
    "query": "What are the benefits of mucuna pruriens for neurological conditions?",
    "k": 5,
    "min_score": 0.7,
    "generate_answer": True
}

response = requests.post("http://localhost:8000/api/similarity_search", json=search_data)
results = response.json()

print(f"Found {len(results['results'])} results")
for result in results['results']:
    print(f"- {result['text'][:100]}... (Score: {result['similarity_score']:.3f})")

if results.get('generated_answer'):
    print(f"\nGenerated Answer: {results['generated_answer']['answer']}")
    print(f"Citations: {results['generated_answer']['citations']}")
```

### 3. Get Journal Information

```python
import requests

journal_id = "mucuna_review_2023"
response = requests.get(f"http://localhost:8000/api/{journal_id}")

if response.status_code == 200:
    journal_data = response.json()
    print(f"Journal: {journal_data['title']}")
    print(f"Total chunks: {journal_data['stats']['total_chunks']}")
    print(f"Sections: {journal_data['stats']['sections']}")
else:
    print(f"Journal not found: {response.status_code}")
```

## Development Tips

### 1. Environment Variables
Make sure to set these in your `.env` file:
- `OPENAI_API_KEY`: Your OpenAI API key
- `CHROMA_PERSIST_DIRECTORY`: Directory for ChromaDB storage
- `SQLITE_DATABASE_PATH`: Path to SQLite database
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### 2. Database Management
The API automatically creates the necessary database tables and ChromaDB collections on startup. No manual setup required.

### 3. Error Handling
The API implements comprehensive error handling:
- Input validation errors return 422
- Not found errors return 404
- External service errors return 503
- Internal errors return 500

### 4. Testing
Run the test suite to ensure everything works:
```bash
pytest tests/
```

### 5. Development Workflow
1. Make changes to the code
2. Run tests to ensure functionality
3. Test endpoints manually or with the test script
4. Check logs for any issues
5. Update documentation as needed

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you've installed all dependencies
2. **OpenAI API errors**: Check your API key and rate limits
3. **Database errors**: Ensure proper file permissions
4. **ChromaDB errors**: Check if the persist directory is writable

### Debug Mode
Set `LOG_LEVEL=DEBUG` in your `.env` file for detailed logging.

### Performance Monitoring
Monitor these metrics:
- Response times for each endpoint
- OpenAI API usage and costs
- Database query performance
- Memory usage for large uploads

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL/TLS certificates installed
- [ ] Rate limiting configured
- [ ] Monitoring and logging set up
- [ ] Backup procedures established
- [ ] Security headers configured
- [ ] CORS policies set
- [ ] Error tracking enabled

## API Documentation

The API automatically generates interactive documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

This documentation includes:
- All endpoint specifications
- Request/response schemas
- Interactive testing interface
- Authentication requirements (when implemented)

## Contributing

When adding new features:
1. Follow the existing code structure
2. Add appropriate tests
3. Update documentation
4. Ensure error handling is comprehensive
5. Test with various input scenarios
