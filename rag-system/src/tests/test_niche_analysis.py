import pytest
from datetime import datetime
from src.services.niche_analysis_service import NicheAnalysisService, NicheAnalysis, ValidationError, NicheAnalysisError

@pytest.fixture
def niche_service():
    return NicheAnalysisService()

@pytest.fixture
def valid_user_input():
    return {
        'topic': 'AI in Healthcare',
        'preferences': {
            'platform': 'twitter',
            'style': 'professional',
            'query_context': 'How is AI used in medical diagnosis?'
        }
    }

@pytest.fixture
def sample_niche_analysis():
    return NicheAnalysis(
        main_topic='AI in Healthcare',
        subtopics=['Medical Diagnosis', 'Patient Care', 'Drug Discovery'],
        keywords=['artificial intelligence', 'healthcare', 'medical diagnosis', 'machine learning', 'patient care'],
        content_style='professional',
        target_platforms=['twitter'],
        generated_at=datetime.now()
    )

def test_validate_user_input(niche_service, valid_user_input):
    """Test input validation with valid input"""
    validated_input = niche_service._validate_user_input(valid_user_input)
    assert validated_input['topic'] == 'AI in Healthcare'
    assert validated_input['preferences']['platform'] == 'twitter'
    assert validated_input['preferences']['style'] == 'professional'
    assert validated_input['preferences']['query_context'] == 'How is AI used in medical diagnosis?'

def test_validate_user_input_missing_topic(niche_service):
    """Test input validation with missing topic"""
    invalid_input = {
        'preferences': {
            'platform': 'twitter',
            'style': 'professional'
        }
    }
    with pytest.raises(ValidationError):
        niche_service._validate_user_input(invalid_input)

def test_validate_user_input_invalid_preferences(niche_service):
    """Test input validation with invalid preferences"""
    invalid_input = {
        'topic': 'AI in Healthcare',
        'preferences': 'not_a_dict'
    }
    with pytest.raises(ValidationError):
        niche_service._validate_user_input(invalid_input)

def test_validate_user_input_default_values(niche_service):
    """Test input validation with missing preferences fields"""
    input_with_missing_fields = {
        'topic': 'AI in Healthcare'
    }
    validated_input = niche_service._validate_user_input(input_with_missing_fields)
    assert validated_input['preferences']['platform'] == 'twitter'
    assert validated_input['preferences']['style'] == 'professional'
    assert validated_input['preferences']['query_context'] == 'AI in Healthcare'

def test_analyze_niche(niche_service, valid_user_input, sample_niche_analysis):
    """Test successful niche analysis"""
    analysis = niche_service.analyze_niche(valid_user_input)
    
    # Verify main topic is set
    assert analysis.main_topic
    assert isinstance(analysis.main_topic, str)
    
    # Verify subtopics are generated
    assert analysis.subtopics
    assert len(analysis.subtopics) >= 3
    assert all(isinstance(topic, str) for topic in analysis.subtopics)
    
    # Verify keywords are generated
    assert analysis.keywords
    assert len(analysis.keywords) >= 5
    assert all(isinstance(keyword, str) for keyword in analysis.keywords)
    
    # Verify style and platforms
    assert analysis.content_style == valid_user_input['preferences']['style']
    assert set(analysis.target_platforms) == set(valid_user_input['preferences']['platform'])
    
    # Verify timestamp
    assert analysis.generated_at

def test_analyze_niche_invalid_input(niche_service):
    """Test niche analysis with invalid input"""
    invalid_inputs = [
        {},  # Empty dict
        {'topic': ''},  # Empty topic
        {'topic': 'AI', 'preferences': None},  # Missing preferences
        {'topic': 'AI', 'preferences': {'platform': [], 'style': ''}},  # Empty preferences
    ]
    
    for invalid_input in invalid_inputs:
        with pytest.raises(NicheAnalysisError):
            niche_service.analyze_niche(invalid_input)

def test_update_analysis(niche_service, valid_user_input, sample_niche_analysis):
    """Test updating existing analysis"""
    updated_input = valid_user_input.copy()
    updated_input['preferences']['platform'].append('twitter')
    
    updated_analysis = niche_service.update_analysis(sample_niche_analysis, updated_input)
    
    # Verify main topic persists
    assert updated_analysis.main_topic == sample_niche_analysis.main_topic
    
    # Verify subtopics and keywords are regenerated
    assert len(updated_analysis.subtopics) >= 3
    assert len(updated_analysis.keywords) >= 5
    
    # Verify updated platforms
    assert 'twitter' in updated_analysis.target_platforms
    
    # Verify timestamp is updated
    assert updated_analysis.generated_at > sample_niche_analysis.generated_at 