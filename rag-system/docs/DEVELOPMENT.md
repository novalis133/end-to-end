# Development Guide: Ollama Integration

## Overview
This document provides detailed information about how the RAG system communicates with Ollama for text embedding and generation. The integration uses Ollama's HTTP API endpoints to perform two main operations:
1. Generating text embeddings
2. Generating contextual responses

## Ollama Configuration
The system uses the following environment variables for Ollama configuration:
```env
OLLAMA_HOST=http://localhost:11434
MODEL_NAME=mistral
```

## Embedding Generation
The `embed_text` method in `RAGService` handles text embedding generation:

```python
def embed_text(self, text: str) -> List[float]:
    try:
        response = requests.post(
            f"{self.ollama_host}/api/embeddings",
            json={
                "model": self.model_name,
                "prompt": text
            }
        )
        response.raise_for_status()
        return response.json()['embedding']
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return []
```

### How it works:
1. Makes a POST request to Ollama's `/api/embeddings` endpoint
2. Sends the text to be embedded and the model name
3. Returns a list of floating-point numbers representing the text embedding
4. Handles errors gracefully by returning an empty list

### Modifying Embedding Generation:
1. **Change Model**: Update `MODEL_NAME` in `.env` to use a different model
2. **Add Parameters**: Extend the JSON payload with additional parameters:
   ```python
   json={
       "model": self.model_name,
       "prompt": text,
       "options": {
           "temperature": 0.7,
           "top_p": 0.9
       }
   }
   ```
3. **Error Handling**: Add more specific error handling:
   ```python
   except requests.exceptions.ConnectionError:
       print("Could not connect to Ollama server")
   except requests.exceptions.HTTPError as e:
       print(f"HTTP error occurred: {e.response.status_code}")
   ```

## Contextual Text Generation
The `generate_with_context` method handles text generation with context:

```python
def generate_with_context(self, prompt: str, context_docs: List[Dict[str, Any]]) -> str:
    try:
        # Format context
        context = "\n\n".join([
            f"Document {i+1}:\n{doc['content']}\nRelevance: {doc['score']:.2f}"
            for i, doc in enumerate(context_docs)
        ])
        
        # Create system message with context
        system_message = f"""You are a helpful assistant. Use the following context to answer the user's question:

{context}

Please provide a detailed and accurate response based on the context above."""
        
        # Generate response
        response = requests.post(
            f"{self.ollama_host}/api/chat",
            json={
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()['message']['content']
    except Exception as e:
        print(f"Error generating text with context: {e}")
        return ""
```

### How it works:
1. Formats the context documents into a structured string
2. Creates a system message that includes the context
3. Makes a POST request to Ollama's `/api/chat` endpoint
4. Uses a chat format with system and user messages
5. Returns the generated text response

### Modifying Text Generation:
1. **Change Context Format**: Modify how context is formatted:
   ```python
   context = "\n---\n".join([
       f"Title: {doc.get('title', 'Untitled')}\nContent: {doc['content']}"
       for doc in context_docs
   ])
   ```

2. **Add Generation Parameters**:
   ```python
   json={
       "model": self.model_name,
       "messages": [
           {"role": "system", "content": system_message},
           {"role": "user", "content": prompt}
       ],
       "options": {
           "temperature": 0.7,
           "top_p": 0.9,
           "max_tokens": 1000
       },
       "stream": False
   }
   ```

3. **Enable Streaming**: For real-time responses:
   ```python
   "stream": True
   ```

## Feature Roadmap

### 1. Enhanced Content Processing
This section focuses on improving how we process and analyze different types of content, not just academic papers. The system will be able to handle:
- Academic papers (PDF, arXiv)
- GitHub repositories (code, documentation)
- Framework documentation
- Technical blog posts
- Release notes
- API documentation

The enhanced processing will provide:
- Better content understanding
- More accurate categorization
- Improved relationship mapping
- Better context for generation

```python
class ContentProcessor:
    def extract_content(self, source: str, content_type: str) -> Dict[str, Any]:
        """Extract structured content from various sources"""
        pass

    def analyze_references(self, content: str, content_type: str) -> List[str]:
        """Extract and analyze references based on content type"""
        pass

    def categorize_content(self, content: str, content_type: str) -> List[str]:
        """Categorize content into relevant topics/subfields"""
        pass

    def calculate_relevance_score(self, content_data: Dict[str, Any]) -> float:
        """Calculate content relevance score based on type and context"""
        pass
```

### 2. Advanced RAG Features
This section enhances the RAG system to better handle different types of content and their unique characteristics. Key improvements include:

- Multi-aspect embeddings for different content types
- Hierarchical content organization
- Metadata extraction specific to content type
- Cross-content relationship analysis
- Version tracking for code and documentation

These improvements will:
- Provide better context for generation
- Improve content retrieval accuracy
- Enable better content organization
- Support version-aware content handling

```python
class EnhancedRAGService:
    def generate_multi_vector_embeddings(self, text: str, content_type: str) -> Dict[str, List[float]]:
        """Generate embeddings for different aspects of content based on type"""
        pass

    def chunk_content(self, content: str, content_type: str) -> List[Dict[str, Any]]:
        """Create hierarchical content chunks based on type"""
        pass

    def extract_metadata(self, content: str, content_type: str) -> Dict[str, Any]:
        """Extract metadata specific to content type"""
        pass

    def analyze_relationships(self, contents: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Analyze relationships between different content types"""
        pass
```

### 3. Content Generation Improvements
This section focuses on generating content that's appropriate for different types of sources and platforms. Features include:

- Platform-specific content generation
- Content type-specific formatting
- Scheduled content distribution
- Performance testing and optimization
- Multi-format content creation

These improvements will:
- Generate more relevant content
- Improve engagement across platforms
- Optimize content delivery
- Provide better content analytics

```python
class ContentGenerator:
    def generate_content(self, source: Dict[str, Any], platform: str) -> List[str]:
        """Generate platform-specific content from various sources"""
        pass

    def generate_summary(self, content: str, content_type: str, style: str) -> str:
        """Generate content in different styles based on type"""
        pass

    def schedule_content(self, content: List[str], schedule: Dict[str, str]):
        """Schedule content posting across platforms"""
        pass

    def test_content(self, variations: List[str], content_type: str) -> Dict[str, float]:
        """A/B test content variations for different types"""
        pass
```

### 4. User Interface and Monitoring
This section focuses on providing better tools for managing and monitoring different types of content. Features include:

- Content type-specific dashboards
- Queue management for different sources
- Performance tracking across platforms
- User feedback collection and analysis
- Content health monitoring

These improvements will:
- Provide better content management
- Enable more effective monitoring
- Improve user experience
- Support better decision making

```python
class Dashboard:
    def display_metrics(self, content_type: str) -> Dict[str, Any]:
        """Display performance metrics for specific content types"""
        pass

    def manage_queue(self, content_type: str) -> List[Dict[str, Any]]:
        """Manage content submission queue by type"""
        pass

    def track_performance(self, content_type: str) -> Dict[str, float]:
        """Track content performance by type"""
        pass

    def collect_feedback(self, content_type: str) -> Dict[str, Any]:
        """Collect and analyze user feedback for specific content types"""
        pass
```

### 5. Integration Enhancements
This section focuses on expanding the system's reach and capabilities through various integrations. Features include:

- Multiple platform support
- Newsletter generation
- Team communication integration
- Webhook support for automation
- API access for external systems

These improvements will:
- Increase content distribution
- Improve team collaboration
- Enable automation
- Support external integration

```python
class IntegrationManager:
    def post_to_platform(self, content: str, platform: str) -> bool:
        """Post content to various platforms"""
        pass

    def generate_newsletter(self, contents: List[Dict[str, Any]]) -> str:
        """Generate newsletter from various content types"""
        pass

    def send_to_team(self, content: str, channel: str, platform: str) -> bool:
        """Send content to team communication platforms"""
        pass

    def handle_webhook(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming webhooks for automation"""
        pass
```

## Implementation Priorities

### Phase 1: Core Enhancements
1. PDF parsing and content extraction
2. Multi-vector embeddings
3. Basic dashboard interface
4. Content scheduling system

### Phase 2: Advanced Features
1. Citation analysis and impact scoring
2. Cross-paper relationship analysis
3. A/B testing framework
4. Multiple social media platform support

### Phase 3: User Experience
1. Advanced dashboard with analytics
2. Content approval workflow
3. User feedback system
4. API documentation and examples

## Technical Considerations

### Performance Optimization
1. Implement caching for embeddings
2. Use batch processing for multiple papers
3. Optimize database queries
4. Implement rate limiting for API calls

### Scalability
1. Use message queues for processing
2. Implement horizontal scaling
3. Add load balancing
4. Optimize storage for large datasets

### Security
1. Implement API key rotation
2. Add rate limiting
3. Secure storage of credentials
4. Add audit logging

## Testing Strategy

### Unit Tests
```python
def test_pdf_extraction():
    """Test PDF content extraction"""
    pass

def test_multi_vector_embeddings():
    """Test multi-vector embedding generation"""
    pass

def test_content_generation():
    """Test content generation in different styles"""
    pass
```

### Integration Tests
```python
def test_end_to_end_workflow():
    """Test complete paper processing workflow"""
    pass

def test_social_media_integration():
    """Test social media platform integration"""
    pass
```

### Performance Tests
```python
def test_processing_speed():
    """Test processing speed for multiple papers"""
    pass

def test_concurrent_requests():
    """Test system under concurrent load"""
    pass
```

## Deployment Considerations

### Infrastructure
1. Containerization with Docker
2. Kubernetes orchestration
3. CI/CD pipeline setup
4. Monitoring and alerting

### Data Management
1. Backup strategy
2. Data retention policies
3. Version control for models
4. Database optimization

### Monitoring
1. Performance metrics
2. Error tracking
3. Usage analytics
4. System health checks 