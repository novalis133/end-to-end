import os
from src.services.rag_service import RAGService
import json
from dotenv import load_dotenv
import pytest
from datetime import datetime
from src.services.pipeline_service import PipelineService
from src.services.niche_analysis_service import NicheAnalysis, NicheAnalysisError, ValidationError

def test_pipeline():
    # Load environment variables
    load_dotenv()
    
    # Initialize RAG service
    rag_service = RAGService()
    
    # Sample paper content
    sample_paper = {
        "title": "Attention Is All You Need",
        "authors": "Vaswani et al.",
        "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train.",
        "content": "The Transformer architecture has revolutionized natural language processing. It uses self-attention mechanisms to process input sequences, allowing for better parallelization and improved performance on various tasks.",
        "source_url": "https://arxiv.org/abs/1706.03762"
    }
    
    # Test embedding generation
    print("\nTesting embedding generation...")
    embedding = rag_service.embed_text(sample_paper["abstract"])
    print(f"Generated embedding of length: {len(embedding)}")
    
    # Test text generation with context
    print("\nTesting text generation with context...")
    context_docs = [{
        "content": sample_paper["abstract"],
        "score": 1.0
    }]
    
    prompt = "Summarize the key innovation of this paper in one sentence."
    generated_text = rag_service.generate_with_context(prompt, context_docs)
    print(f"\nGenerated summary:\n{generated_text}")
    
    # Test Twitter post generation (without posting)
    print("\nTesting Twitter post generation...")
    twitter_post = rag_service.create_twitter_post(
        sample_paper["abstract"], 
        context_docs,
        source_url=sample_paper["source_url"]
    )
    print(f"\nGenerated Twitter post:\n{twitter_post}")

@pytest.fixture
def pipeline_service():
    return PipelineService()

@pytest.fixture
def valid_request_data():
    return {
        'account_id': 'test_account_123',
        'topic': 'AI in Healthcare',
        'query': 'How is AI used in medical diagnosis?',
        'platform': 'twitter'
    }

def test_process_content_request(pipeline_service, valid_request_data):
    """Test the complete content request pipeline"""
    try:
        result = pipeline_service.process_content_request(
            account_id=valid_request_data['account_id'],
            topic=valid_request_data['topic'],
            query=valid_request_data['query'],
            platform=valid_request_data['platform']
        )
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'account_id' in result
        assert 'post_id' in result
        assert 'content' in result
        assert 'platform' in result
        assert 'generated_at' in result
        assert 'performance_metrics' in result
    except NicheAnalysisError:
        # Skip test if Ollama service is not available
        pytest.skip("Ollama service not available")

def test_process_content_request_missing_platform(pipeline_service, valid_request_data):
    """Test content request with missing platform (should default to twitter)"""
    try:
        result = pipeline_service.process_content_request(
            account_id=valid_request_data['account_id'],
            topic=valid_request_data['topic'],
            query=valid_request_data['query']
        )
        assert result['platform'] == 'twitter'
    except NicheAnalysisError:
        # Skip test if Ollama service is not available
        pytest.skip("Ollama service not available")

def test_process_content_request_invalid_platform(pipeline_service, valid_request_data):
    """Test content request with invalid platform"""
    with pytest.raises(ValueError, match="Invalid platform"):
        pipeline_service.process_content_request(
            account_id=valid_request_data['account_id'],
            topic=valid_request_data['topic'],
            query=valid_request_data['query'],
            platform='invalid_platform'
        )

def test_process_content_request_missing_query(pipeline_service, valid_request_data):
    """Test content request with missing query (should use topic as query)"""
    try:
        result = pipeline_service.process_content_request(
            account_id=valid_request_data['account_id'],
            topic=valid_request_data['topic'],
            platform=valid_request_data['platform']
        )
        assert isinstance(result['content'], str)
        assert len(result['content']) > 0
    except NicheAnalysisError:
        # Skip test if Ollama service is not available
        pytest.skip("Ollama service not available")

def test_process_content_request_error_handling(pipeline_service):
    """Test error handling in content request processing"""
    with pytest.raises(ValidationError):
        pipeline_service.process_content_request(
            account_id='',
            topic='',
            query='',
            platform='twitter'
        )

if __name__ == "__main__":
    test_pipeline() 