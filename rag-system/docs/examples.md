# RAG System Examples

## Working with Research Papers

```python
from services.rag_service import RAGService
from datetime import datetime

# Initialize the service
rag = RAGService()

# Example paper data
paper = {
    "title": "Attention Is All You Need",
    "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
    "authors": ["Vaswani", "Shazeer", "Parmar", "Uszkoreit", "Jones", "Gomez", "Kaiser", "Polosukhin"],
    "year": 2017
}

# Store the paper
content = f"Title: {paper['title']}\nAbstract: {paper['abstract']}"
metadata = {
    "title": paper["title"],
    "authors": paper["authors"],
    "year": paper["year"],
    "source": "arxiv"
}
doc_id = rag.store_document(content, metadata, "paper")

# Query similar papers
similar_papers = rag.retrieve_similar_documents(
    query="What are the key innovations in transformer architecture?",
    doc_type="paper"
)

# Generate a summary
summary = rag.generate_with_context(
    "Summarize the key innovations in transformer architecture",
    similar_papers
)

# Create a Twitter post
tweet = rag.create_twitter_post(
    "New insights into transformer architecture",
    similar_papers
)
```

## Working with GitHub Repositories

```python
from services.rag_service import RAGService

# Initialize the service
rag = RAGService()

# Example repo data
repo = {
    "name": "transformers",
    "description": "State-of-the-art Machine Learning for JAX, PyTorch and TensorFlow",
    "topics": ["nlp", "machine-learning", "deep-learning", "pytorch"],
    "stars": 100000,
    "owner": "huggingface"
}

# Store the repo
content = f"Name: {repo['name']}\nDescription: {repo['description']}\nTopics: {', '.join(repo['topics'])}"
metadata = {
    "name": repo["name"],
    "owner": repo["owner"],
    "stars": repo["stars"],
    "source": "github"
}
doc_id = rag.store_document(content, metadata, "repo")

# Query similar repos
similar_repos = rag.retrieve_similar_documents(
    query="What are the most popular NLP libraries?",
    doc_type="repo"
)

# Generate a summary
summary = rag.generate_with_context(
    "What are the key features of popular NLP libraries?",
    similar_repos
)

# Create a Twitter post
tweet = rag.create_twitter_post(
    "Top NLP libraries and frameworks",
    similar_repos
)
```

## Working with User Data

```python
from services.rag_service import RAGService

# Initialize the service
rag = RAGService()

# Example user data
user = {
    "name": "John Doe",
    "interests": ["machine learning", "natural language processing", "deep learning"],
    "publications": ["Paper on Transformers", "BERT Implementation Guide"],
    "followers": 1000
}

# Store user data
content = f"Name: {user['name']}\nInterests: {', '.join(user['interests'])}\nPublications: {', '.join(user['publications'])}"
metadata = {
    "name": user["name"],
    "followers": user["followers"],
    "source": "user_profile"
}
doc_id = rag.store_document(content, metadata, "user")

# Query similar users
similar_users = rag.retrieve_similar_documents(
    query="Who are experts in machine learning?",
    doc_type="user"
)

# Generate a summary
summary = rag.generate_with_context(
    "What are the research interests of ML experts?",
    similar_users
)

# Create a Twitter post
tweet = rag.create_twitter_post(
    "Meet the ML experts",
    similar_users
)
```

## Creating Twitter Posts

```python
from services.rag_service import RAGService

# Initialize the service
rag = RAGService()

# Example content and context
content = "New research on Large Language Models"
context_docs = [
    {
        "content": "Paper introduces a new architecture for LLMs",
        "metadata": {"source": "arxiv"},
        "score": 0.9
    },
    {
        "content": "LLMs show improved performance on various tasks",
        "metadata": {"source": "arxiv"},
        "score": 0.8
    }
]

# Create a Twitter post
tweet = rag.create_twitter_post(content, context_docs)
print(tweet)
```

## Batch Processing

```python
from services.rag_service import RAGService
import json

# Initialize the service
rag = RAGService()

# Load data from a file
with open('papers.json', 'r') as f:
    papers = json.load(f)

# Store multiple documents
for paper in papers:
    content = f"Title: {paper['title']}\nAbstract: {paper['abstract']}"
    metadata = {
        "title": paper["title"],
        "authors": paper["authors"],
        "year": paper["year"],
        "source": "arxiv"
    }
    rag.store_document(content, metadata, "paper")

# Process multiple queries
queries = [
    "What are the latest developments in transformers?",
    "How do LLMs handle context?",
    "What are the challenges in NLP?"
]

for query in queries:
    similar_docs = rag.retrieve_similar_documents(query, doc_type="paper")
    summary = rag.generate_with_context(query, similar_docs)
    tweet = rag.create_twitter_post(query, similar_docs)
    print(f"\nQuery: {query}")
    print(f"Summary: {summary}")
    print(f"Tweet: {tweet}")
``` 