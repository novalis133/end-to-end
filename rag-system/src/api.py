from flask import Flask, request, jsonify
from services.pipeline_service import PipelineService
from services.niche_analysis_service import NicheAnalysisError
import logging
import os
from dotenv import load_dotenv
from typing import Dict, Any
from werkzeug.exceptions import HTTPException, BadRequest
import json
from pymongo import MongoClient
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize pipeline service
pipeline_service = PipelineService()

class APIError(Exception):
    """Base class for API errors"""
    def __init__(self, message, status_code=400, error_code=None, details=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details

class ValidationError(APIError):
    """Raised when input validation fails"""
    def __init__(self, message, details=None):
        super().__init__(message, 400, 'VALIDATION_ERROR', details)

class ServiceError(APIError):
    """Raised when a service operation fails"""
    def __init__(self, message, details=None):
        super().__init__(message, 500, 'SERVICE_ERROR', details)

@app.errorhandler(APIError)
def handle_api_error(error):
    """Handle API errors"""
    response = {
        'error': {
            'code': error.error_code,
            'message': error.message,
            'details': error.details
        }
    }
    return jsonify(response), error.status_code

@app.errorhandler(HTTPException)
def handle_http_error(error):
    """Handle HTTP errors"""
    response = {
        'error': {
            'code': 'HTTP_ERROR',
            'message': error.description,
            'details': None
        }
    }
    return jsonify(response), error.code

@app.errorhandler(Exception)
def handle_unexpected_error(error):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error: {str(error)}", exc_info=True)
    response = {
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': 'An unexpected error occurred',
            'details': str(error)
        }
    }
    return jsonify(response), 500

def validate_json_content():
    """Validate that request has JSON content"""
    if not request.is_json:
        raise ValidationError(
            "Content-Type must be application/json",
            details={"content_type": request.content_type}
        )
    
    try:
        request.get_json()
    except BadRequest as e:
        raise ValidationError(
            "Invalid JSON format",
            details={"error": str(e)}
        )

def validate_required_fields(data: Dict[str, Any], required_fields: list):
    """Validate that all required fields are present"""
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValidationError(
            "Missing required fields",
            details={"missing_fields": missing_fields}
        )

def validate_platform(platform: str):
    """Validate platform value"""
    valid_platforms = ['twitter', 'linkedin', 'medium', 'github']
    if platform not in valid_platforms:
        raise ValidationError(
            "Invalid platform",
            details={
                "platform": platform,
                "valid_platforms": valid_platforms
            }
        )

@app.route('/api/v1/generate', methods=['POST'])
def generate_content():
    """Generate content based on user input."""
    # Validate JSON content
    if not request.is_json:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Content-Type must be application/json',
                'details': None
            }
        }), 400

    try:
        data = request.get_json()
    except BadRequest:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid JSON format',
                'details': None
            }
        }), 400
    
    # Validate required fields
    required_fields = ['account_id', 'topic', 'query']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Missing required fields',
                'details': {'missing_fields': missing_fields}
            }
        }), 400

    # Extract and validate platform
    platform = data.get('platform', 'twitter')
    if platform not in ['twitter', 'linkedin', 'facebook']:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid platform',
                'details': {'platform': platform}
            }
        }), 400

    # Extract content style with default
    content_style = data.get('content_style', 'professional')
    valid_styles = ['professional', 'casual', 'technical', 'informal', 'formal', 'friendly']
    if content_style not in valid_styles:
        return jsonify({
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid content style',
                'details': {
                    'content_style': content_style,
                    'valid_styles': valid_styles
                }
            }
        }), 400

    try:
        # Process the request through the pipeline
        result = pipeline_service.process_content_request(
            account_id=data['account_id'],
            topic=data['topic'],
            query=data['query'],
            platform=platform,
            content_style=content_style
        )

        return jsonify({
            'success': True,
            'data': result
        }), 200

    except NicheAnalysisError as e:
        logger.error(f"Niche analysis error: {str(e)}")
        return jsonify({
            'error': {
                'code': 'NICHE_ANALYSIS_ERROR',
                'message': str(e),
                'details': None
            }
        }), 400

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Internal server error',
                'details': str(e)
            }
        }), 500

# Run the server
if __name__ == '__main__':
    try:
        # Check MongoDB connection
        client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017'))
        client.server_info()
        logger.info("MongoDB connection successful")
        
        # Check Ollama connection
        ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        response = requests.get(f"{ollama_host}/api/tags")
        if response.status_code == 200:
            logger.info("Ollama connection successful")
        else:
            raise Exception("Ollama service is not running")
            
        logger.info("Starting API server on http://127.0.0.1:5001")
        app.run(host='127.0.0.1', port=5001, debug=True)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise