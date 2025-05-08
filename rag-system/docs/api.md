# RAG Service API Documentation

## RAGService Class

The main class that provides all RAG functionality.

### Initialization

```python
from services.rag_service import RAGService

rag = RAGService()
```

### Methods

#### embed_text(text: str) -> List[float]

Generates embeddings for text using Ollama.

**Parameters:**
- `text` (str): Text to embed

**Returns:**
- `List[float]`: Embedding vector

**Example:**
```python
embedding = rag.embed_text("This is a test document")
```

#### store_document(content: str, metadata: Dict[str, Any], doc_type: str) -> str

Stores a document with its embeddings and metadata.

**Parameters:**
- `content` (str): Document content
- `metadata` (Dict[str, Any]): Document metadata
- `doc_type` (str): Type of document (e.g., 'paper', 'repo', 'user')

**Returns:**
- `str`: Document ID

**Example:**
```python
doc_id = rag.store_document(
    content="Document content",
    metadata={"title": "Test Document", "author": "Test Author"},
    doc_type="test"
)
```

#### retrieve_similar_documents(query: str, doc_type: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]

Retrieves similar documents based on a query.

**Parameters:**
- `query` (str): Query text
- `doc_type` (Optional[str]): Filter by document type
- `limit` (int): Maximum number of results

**Returns:**
- `List[Dict[str, Any]]`: List of similar documents with metadata

**Example:**
```python
similar_docs = rag.retrieve_similar_documents(
    query="What is machine learning?",
    doc_type="educational"
)
```

#### generate_with_context(prompt: str, context_docs: List[Dict[str, Any]]) -> str

Generates text using Ollama with context from similar documents.

**Parameters:**
- `prompt` (str): User prompt
- `context_docs` (List[Dict[str, Any]]): Context documents

**Returns:**
- `str`: Generated text

**Example:**
```python
response = rag.generate_with_context(
    prompt="What are Large Language Models?",
    context_docs=similar_docs
)
```

#### create_twitter_post(content: str, context_docs: List[Dict[str, Any]]) -> str

Generates a Twitter post using context from similar documents.

**Parameters:**
- `content` (str): Content to post about
- `context_docs` (List[Dict[str, Any]]): Context documents

**Returns:**
- `str`: Formatted Twitter post

**Example:**
```python
tweet = rag.create_twitter_post(
    content="New research on LLMs",
    context_docs=similar_docs
)
```

## Data Structures

### Document Structure

```python
{
    "content": str,           # Document content
    "metadata": Dict[str, Any],  # Document metadata
    "doc_type": str,          # Document type
    "score": float           # Similarity score (for retrieved documents)
}
```

### Metadata Structure

```python
{
    "title": str,            # Document title
    "source": str,           # Data source
    "author": str,           # Author name
    "created_at": datetime,  # Creation timestamp
    # Additional metadata fields as needed
}
```

## Error Handling

The service handles errors gracefully and provides informative error messages. Common errors include:

- Connection errors with MongoDB or Ollama
- Invalid document types
- Empty or invalid queries
- API rate limits

## Best Practices

1. **Document Types**
   - Use consistent document types
   - Include relevant metadata
   - Keep content concise but informative

2. **Querying**
   - Use specific queries for better results
   - Filter by document type when appropriate
   - Adjust limit based on use case

3. **Context Generation**
   - Provide clear prompts
   - Include relevant context documents
   - Monitor response quality

4. **Twitter Posts**
   - Keep content focused
   - Include relevant hashtags
   - Stay within character limits 