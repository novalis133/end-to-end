import pytest
from services.rag_service import RAGService
import os
from dotenv import load_dotenv
from datetime import datetime
from src.services.niche_analysis_service import NicheAnalysisError

# Load test environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env.test'))

@pytest.fixture
def rag_service():
    """Create a RAG service instance for testing."""
    service = RAGService()
    yield service
    # Cleanup after tests
    if hasattr(service, 'db'):
        service.db.drop_database(os.getenv('DB_NAME'))

@pytest.fixture
def test_document():
    """Create a test document."""
    return {
        "content": "This is a test document about language models and transformers.",
        "metadata": {
            "title": "Test Document",
            "source": "test",
            "date": "2024-01-01"
        }
    }

@pytest.fixture
def sample_document():
    return {
        'content': 'AI in healthcare is revolutionizing medical diagnosis through machine learning algorithms.',
        'metadata': {
            'title': 'AI in Medical Diagnosis',
            'source': 'test_source',
            'date': datetime.now().isoformat()
        }
    }

def test_get_embeddings(rag_service):
    """Test embedding generation."""
    text = "Test text for embedding"
    embeddings = rag_service.get_embeddings(text)
    assert isinstance(embeddings, list)
    assert len(embeddings) == 300  # Assuming 300-dimensional embeddings

def test_store_document(rag_service, test_document):
    """Test document storage."""
    doc_id = rag_service.store_document(
        test_document["content"],
        test_document["metadata"]
    )
    assert isinstance(doc_id, str)
    assert len(doc_id) > 0

def test_retrieve_documents(rag_service, test_document):
    """Test document retrieval."""
    # First store a document
    doc_id = rag_service.store_document(
        test_document["content"],
        test_document["metadata"]
    )
    
    # Then retrieve similar documents
    query = "language models"
    similar_docs = rag_service.retrieve_documents(query)
    
    assert isinstance(similar_docs, list)
    assert len(similar_docs) > 0
    assert "content" in similar_docs[0]
    assert "metadata" in similar_docs[0]

def test_generate_with_context(rag_service):
    """Test content generation with context."""
    context = "Recent advances in transformer architecture"
    query = "What are the key improvements?"
    
    result = rag_service.generate_with_context(context, query)
    assert isinstance(result, str)
    assert len(result) > 0

def test_create_twitter_post(rag_service):
    """Test Twitter post creation."""
    content = "Test content for Twitter post"
    style = "professional"
    
    post = rag_service.create_twitter_post(content, style)
    assert isinstance(post, dict)
    assert "content" in post
    assert "hashtags" in post
    assert "mentions" in post
    assert len(post["content"]) <= 280  # Twitter character limit

def test_empty_content(rag_service):
    """Test handling of empty content."""
    with pytest.raises(ValueError):
        rag_service.store_document("", {})

def test_empty_query(rag_service):
    """Test handling of empty query."""
    with pytest.raises(ValueError):
        rag_service.retrieve_documents("")

def test_store_account(rag_service):
    """Test storing a new account"""
    account_id = 'test_account_123'
    result = rag_service.store_account(account_id)
    assert isinstance(result, str)

def test_store_preferences(rag_service):
    """Test storing account preferences"""
    account_id = 'test_account_123'
    preferences = {
        'niche': 'Healthcare AI',
        'subtopics': ['Medical Diagnosis', 'Patient Care'],
        'keywords': ['AI', 'healthcare', 'diagnosis'],
        'style': 'professional',
        'platforms': ['twitter', 'linkedin']
    }
    result = rag_service.store_preferences(account_id, preferences)
    assert isinstance(result, str)

def test_store_resource(rag_service, sample_document):
    """Test storing a new resource"""
    account_id = 'test_account_123'
    result = rag_service.store_resource(
        account_id=account_id,
        content=sample_document['content'],
        metadata=sample_document['metadata']
    )
    assert isinstance(result, str)

def test_store_post(rag_service):
    """Test storing a generated post"""
    account_id = 'test_account_123'
    resource_id = 'test_resource_123'
    content = 'AI is transforming healthcare through advanced diagnostic tools.'
    platform = 'twitter'
    metadata = {
        'style': 'professional',
        'generated_at': datetime.now().isoformat()
    }
    result = rag_service.store_post(
        account_id=account_id,
        resource_id=resource_id,
        content=content,
        platform=platform,
        metadata=metadata
    )
    assert isinstance(result, str)

def test_get_account_preferences(rag_service):
    """Test retrieving account preferences"""
    account_id = 'test_account_123'
    preferences = rag_service.get_account_preferences(account_id)
    assert isinstance(preferences, dict)

def test_get_resource(rag_service):
    """Test retrieving a stored resource"""
    resource_id = 'test_resource_123'
    resource = rag_service.get_resource(resource_id)
    assert isinstance(resource, dict)

def test_create_twitter_post(rag_service):
    """Test creating a Twitter post"""
    content = 'AI in healthcare is revolutionizing medical diagnosis.'
    style = 'professional'
    result = rag_service.create_twitter_post(content, style)
    assert isinstance(result, dict)
    assert 'content' in result
    assert isinstance(result['content'], str)
    assert len(result['content']) <= 280  # Twitter character limit

def test_generate_with_context(rag_service):
    """Test generating content with context"""
    context = 'AI in healthcare is transforming medical diagnosis.'
    query = 'How is AI used in medical diagnosis?'
    result = rag_service.generate_with_context(context, query)
    assert isinstance(result, str)
    assert len(result) > 0 