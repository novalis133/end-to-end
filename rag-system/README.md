# RAG System API

A Retrieval-Augmented Generation (RAG) system for generating platform-specific content based on user topics and preferences.

## Features

- Content generation for multiple platforms (Twitter, LinkedIn, Facebook)
- Niche analysis and topic exploration
- Resource collection and management
- MongoDB integration for data persistence
- Ollama integration for text generation

## Prerequisites

- Python 3.11+
- MongoDB
- Ollama (with mistral model)

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the root directory with:

```env
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
MODEL_NAME=mistral

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017
DB_NAME=llm_papers
```

## Usage

1. Start MongoDB service
2. Start Ollama service with mistral model
3. Run the API:
   ```bash
   cd src
   python api.py
   ```

The API will be available at `http://127.0.0.1:5001`

### Generate Content

```bash
curl -X POST http://127.0.0.1:5001/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "test123",
    "topic": "AI in Healthcare",
    "query": "How is AI used in medical diagnosis?",
    "platform": "twitter"
  }'
```

## Project Structure

```
rag-system/
├── .gitignore           # Git ignore file
├── requirements.txt     # Python dependencies
├── README.md           # Project documentation
└── src/
    ├── api.py          # Main API file
    └── services/
        ├── niche_analysis_service.py
        ├── pipeline_service.py
        ├── rag_service.py
        └── resource_collection_service.py
```

## API Endpoints

### POST /api/v1/generate

Generates content based on user input.

**Request Body:**
```json
{
    "account_id": "string",
    "topic": "string",
    "query": "string",
    "platform": "string"  // "twitter", "linkedin", or "facebook"
}
```

**Response:**
```json
{
    "data": {
        "account_id": "string",
        "post_id": "string",
        "content": "string",
        "platform": "string",
        "generated_at": "string",
        "performance_metrics": {
            "views": 0,
            "likes": 0,
            "shares": 0,
            "comments": 0
        }
    }
}
``` 