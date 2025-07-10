"""
Test script to verify the API setup and basic functionality.
Run this after setting up the environment to ensure everything works.
"""
import asyncio
import aiohttp
import json
import sys
from pathlib import Path

API_BASE_URL = "http://localhost:8000"

async def test_health_check():
    """Test the health check endpoint."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Health check passed")
                    return True
                else:
                    print(f"❌ Health check failed with status {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

async def test_upload_endpoint():
    """Test the upload endpoint with sample data."""
    sample_data = {
        "schema_version": "1.0",
        "chunks": [
            {
                "chunk_id": "test_chunk_1",
                "text": "This is a test chunk about mucuna pruriens. It contains sample text for testing the embedding generation and storage functionality.",
                "chunk_index": 0,
                "source_doc_id": "test_doc_1",
                "journal_name": "Test Journal",
                "year": 2023,
                "section": "Introduction"
            }
        ]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{API_BASE_URL}/api/upload", json=sample_data) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Upload test passed: {data.get('message', 'Success')}")
                    return True
                else:
                    error_data = await response.text()
                    print(f"❌ Upload test failed with status {response.status}: {error_data}")
                    return False
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        return False

async def test_search_endpoint():
    """Test the search endpoint."""
    search_data = {
        "query": "mucuna pruriens benefits",
        "k": 5,
        "generate_answer": False
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{API_BASE_URL}/api/similarity_search", json=search_data) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Search test passed: Found {len(data.get('results', []))} results")
                    return True
                else:
                    error_data = await response.text()
                    print(f"❌ Search test failed with status {response.status}: {error_data}")
                    return False
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🔍 Testing GenAI Labs API...")
    print("Make sure the API is running on http://localhost:8000")
    print("You can start it with: python run.py")
    print()
    
    # Wait for user confirmation
    input("Press Enter to continue with tests...")
    
    tests = [
        ("Health Check", test_health_check),
        ("Upload Endpoint", test_upload_endpoint),
        ("Search Endpoint", test_search_endpoint)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        if await test_func():
            passed += 1
        else:
            print(f"💡 Make sure you have:")
            print("   - Set OPENAI_API_KEY in .env file")
            print("   - Started the API server")
            print("   - Installed all dependencies")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your API is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the setup and try again.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
