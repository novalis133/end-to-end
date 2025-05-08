import pytest
import sys
import os
from dotenv import load_dotenv
from datetime import datetime
from src.services.niche_analysis_service import NicheAnalysisService
from src.services.niche_analysis_service import NicheAnalysis

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load test environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env.test'))

@pytest.fixture
def client():
    from api import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def runner():
    from api import app
    return app.test_cli_runner()

@pytest.fixture
def valid_user_input():
    return {
        'topic': 'AI in Medical Diagnosis',
        'preferences': {
            'platform': ['linkedin', 'medium'],
            'style': 'technical',
            'audience': 'healthcare professionals'
        }
    }

@pytest.fixture
def niche_service():
    return NicheAnalysisService()

@pytest.fixture
def sample_niche_analysis():
    return NicheAnalysis(
        main_topic='AI in Medical Diagnosis',
        subtopics=[
            'Machine Learning for Disease Detection',
            'Medical Image Analysis',
            'Clinical Decision Support Systems',
            'Predictive Analytics in Healthcare'
        ],
        keywords=[
            'artificial intelligence',
            'medical diagnosis',
            'healthcare AI',
            'machine learning',
            'clinical analytics',
            'diagnostic algorithms'
        ],
        content_style='technical',
        target_platforms=['linkedin', 'medium'],
        generated_at=datetime.now()
    ) 