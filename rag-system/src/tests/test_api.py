import pytest
import sys
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from flask import Flask
from src.api import app
from src.services.pipeline_service import PipelineService
from src.services.niche_analysis_service import NicheAnalysisError

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load test environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env.test'))

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def error_client():
    """Test client with error-raising pipeline service"""
    # Import NicheAnalysisError at the top level
    from src.services.niche_analysis_service import NicheAnalysisError

    class TestPipelineService:
        def process_content_request(self, account_id, topic, query, platform):
            # Raise the error directly
            raise NicheAnalysisError("Test error")

    # Replace the pipeline service
    original_service = app.pipeline_service
    app.pipeline_service = TestPipelineService()
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client

    # Restore the original service
    app.pipeline_service = original_service

@pytest.fixture
def mock_pipeline_service(mocker):
    """Fixture for mocked pipeline service."""
    mock_pipeline = mocker.Mock()
    mock_pipeline.process_content_request.side_effect = NicheAnalysisError("Test error")
    # Replace the pipeline service in the app
    original_service = app.pipeline_service
    app.pipeline_service = mock_pipeline
    yield mock_pipeline
    # Restore the original service
    app.pipeline_service = original_service

def test_generate_endpoint_success(client, mocker):
    """Test successful content generation."""
    # Mock the pipeline service
    mock_pipeline = mocker.Mock(spec=PipelineService)
    mock_pipeline.process_content_request.return_value = {
        'account_id': 'test_account',
        'post_id': 'test_post',
        'resource_id': 'test_resource',
        'content': 'Test content',
        'platform': 'twitter',
        'generated_at': '2024-01-01T00:00:00',
        'performance_metrics': {}
    }
    
    # Replace the pipeline service in the app
    app.pipeline_service = mock_pipeline
    
    response = client.post('/api/v1/generate', 
                         json={
                             'account_id': 'test_account',
                             'topic': 'AI in Healthcare',
                             'query': 'How is AI used in medical diagnosis?',
                             'platform': 'twitter'
                         },
                         headers={'Content-Type': 'application/json'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'success' in data
    assert data['success'] is True
    assert 'data' in data
    result = data['data']
    assert 'account_id' in result
    assert 'post_id' in result
    assert 'content' in result
    assert result['platform'] == 'twitter'

def test_generate_endpoint_missing_fields(client):
    """Test handling of missing required fields."""
    response = client.post('/api/v1/generate', 
                         json={'topic': 'AI in Healthcare'},
                         headers={'Content-Type': 'application/json'})
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['code'] == 'VALIDATION_ERROR'
    assert 'missing_fields' in data['error']['details']

def test_generate_endpoint_invalid_platform(client):
    """Test handling of invalid platform."""
    response = client.post('/api/v1/generate', 
                         json={
                             'account_id': 'test_account',
                             'topic': 'AI in Healthcare',
                             'query': 'How is AI used in medical diagnosis?',
                             'platform': 'invalid_platform'
                         },
                         headers={'Content-Type': 'application/json'})
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['code'] == 'VALIDATION_ERROR'
    assert 'platform' in data['error']['details']

def test_generate_endpoint_error_handling(client, mock_pipeline_service):
    """Test error handling in the pipeline."""
    response = client.post('/api/v1/generate',
                         json={
                             'account_id': 'test_account',
                             'topic': 'AI in Healthcare',
                             'query': 'How is AI used in medical diagnosis?',
                             'platform': 'twitter'
                         },
                         headers={'Content-Type': 'application/json'})
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['code'] == 'NICHE_ANALYSIS_ERROR'
    assert 'Test error' in data['error']['message']

def test_invalid_json(client):
    """Test handling of invalid JSON"""
    response = client.post('/api/v1/generate', 
                         data='invalid json',
                         headers={'Content-Type': 'application/json'})
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['code'] == 'VALIDATION_ERROR'

def test_missing_fields(client):
    """Test handling of missing required fields."""
    response = client.post('/api/v1/generate', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['code'] == 'VALIDATION_ERROR'
    assert 'missing_fields' in data['error']['details']

def test_invalid_platform(client):
    """Test handling of invalid platform."""
    response = client.post('/api/v1/generate', json={
        'account_id': 'test_account',
        'topic': 'AI in Healthcare',
        'query': 'How is AI used in medical diagnosis?',
        'platform': 'invalid_platform'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error']['code'] == 'VALIDATION_ERROR'
    assert 'platform' in data['error']['details']

if __name__ == '__main__':
    pytest.main() 