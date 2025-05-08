import os
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from dotenv import load_dotenv
import requests
import json
from datetime import datetime
import pymongo
import logging

load_dotenv()

class RAGService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        try:
            # Initialize MongoDB connection
            self.mongo_client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017'))
            self.db = self.mongo_client[os.getenv('DB_NAME', 'llm_papers')]
            
            # Collections for different data types
            self.accounts = self.db.accounts
            self.preferences = self.db.preferences
            self.resources = self.db.resources
            self.posts = self.db.posts
            
            # Test MongoDB connection
            self.mongo_client.server_info()
            
            # Ollama configuration
            self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
            self.model_name = os.getenv('MODEL_NAME', 'gemma:7b')
            
            # Set up MongoDB methods
            self._setup_mongodb_methods()
            
        except Exception as e:
            print(f"Warning: MongoDB connection failed - {str(e)}")
            print("Using in-memory storage for testing")
            self._setup_inmemory_storage()
    
    def _setup_mongodb_methods(self):
        """Set up MongoDB methods."""
        def store_account(account_id: str) -> str:
            account_data = {
                'account_id': account_id,
                'created_at': datetime.now()
            }
            result = self.accounts.insert_one(account_data)
            return str(result.inserted_id)
        
        def store_preferences(account_id: str, preferences: Dict[str, Any]) -> str:
            preference_data = {
                'account_id': account_id,
                'preference_id': f"pref_{datetime.now().timestamp()}",
                'niche': preferences.get('niche'),
                'subtopics': preferences.get('subtopics', []),
                'generated_keywords': preferences.get('keywords', []),
                'content_style': preferences.get('style', 'professional'),
                'platforms': preferences.get('platforms', ['twitter']),
                'created_at': datetime.now()
            }
            result = self.preferences.insert_one(preference_data)
            return str(result.inserted_id)
        
        def store_resource(account_id: str, resource_data: Dict[str, Any]) -> str:
            resource = {
                'account_id': account_id,
                'resource_id': f"res_{datetime.now().timestamp()}",
                'content': resource_data.get('content'),
                'metadata': resource_data.get('metadata', {}),
                'keywords': resource_data.get('keywords', []),
                'usage_count': 0,
                'last_used': None,
                'created_at': datetime.now()
            }
            result = self.resources.insert_one(resource)
            return str(result.inserted_id)
        
        def store_post(account_id: str, resource_id: str, content: str, platform: str, metadata: Dict[str, Any]) -> str:
            post_data = {
                'account_id': account_id,
                'post_id': f"post_{datetime.now().timestamp()}",
                'resource_id': resource_id,
                'content': content,
                'platform': platform,
                'generated_at': datetime.now(),
                'performance_metrics': {
                    'views': 0,
                    'likes': 0,
                    'shares': 0,
                    'comments': 0
                },
                'platform_specific_metadata': metadata.get('platform_specific', {}),
                'created_at': datetime.now()
            }
            result = self.posts.insert_one(post_data)
            return str(result.inserted_id)
        
        def get_account_preferences(account_id: str) -> Dict[str, Any]:
            preferences = self.preferences.find_one(
                {'account_id': account_id},
                sort=[('created_at', -1)]
            )
            return preferences if preferences else {}
        
        def get_resource(resource_id: str) -> Optional[Dict[str, Any]]:
            resource = self.resources.find_one({'resource_id': resource_id})
            return resource if resource else None
        
        # Assign methods
        self.store_account = store_account
        self.store_preferences = store_preferences
        self.store_resource = store_resource
        self.store_post = store_post
        self.get_account_preferences = get_account_preferences
        self.get_resource = get_resource
    
    def _setup_inmemory_storage(self):
        """Set up in-memory storage for testing."""
        self._accounts = {}
        self._preferences = {}
        self._resources = {}
        self._posts = {}
        
        def store_account(account_id: str) -> str:
            data = {
                'account_id': account_id,
                'created_at': datetime.now()
            }
            self._accounts[account_id] = data
            return account_id
        
        def store_preferences(account_id: str, preferences: Dict[str, Any]) -> str:
            preference_id = f"pref_{datetime.now().timestamp()}"
            data = {
                'account_id': account_id,
                'preference_id': preference_id,
                'niche': preferences.get('niche'),
                'subtopics': preferences.get('subtopics', []),
                'generated_keywords': preferences.get('keywords', []),
                'content_style': preferences.get('style', 'professional'),
                'platforms': preferences.get('platforms', ['twitter']),
                'created_at': datetime.now()
            }
            self._preferences[preference_id] = data
            return preference_id
        
        def store_resource(account_id: str, resource_data: Dict[str, Any]) -> str:
            resource_id = f"res_{datetime.now().timestamp()}"
            data = {
                'account_id': account_id,
                'resource_id': resource_id,
                'content': resource_data.get('content'),
                'metadata': resource_data.get('metadata', {}),
                'keywords': resource_data.get('keywords', []),
                'usage_count': 0,
                'last_used': None,
                'created_at': datetime.now()
            }
            self._resources[resource_id] = data
            return resource_id
        
        def store_post(account_id: str, resource_id: str, content: str, platform: str, metadata: Dict[str, Any]) -> str:
            post_id = f"post_{datetime.now().timestamp()}"
            data = {
                'account_id': account_id,
                'post_id': post_id,
                'resource_id': resource_id,
                'content': content,
                'platform': platform,
                'generated_at': datetime.now(),
                'performance_metrics': {
                    'views': 0,
                    'likes': 0,
                    'shares': 0,
                    'comments': 0
                },
                'platform_specific_metadata': metadata.get('platform_specific', {}),
                'created_at': datetime.now()
            }
            self._posts[post_id] = data
            return post_id
        
        def get_account_preferences(account_id: str) -> Dict[str, Any]:
            for pref in self._preferences.values():
                if pref['account_id'] == account_id:
                    return pref
            return {}
        
        def get_resource(resource_id: str) -> Optional[Dict[str, Any]]:
            return self._resources.get(resource_id)
        
        # Assign methods
        self.store_account = store_account
        self.store_preferences = store_preferences
        self.store_resource = store_resource
        self.store_post = store_post
        self.get_account_preferences = get_account_preferences
        self.get_resource = get_resource

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embeddings for text using Ollama.
        
        Args:
            text (str): Text to embed
            
        Returns:
            List[float]: Embedding vector
        """
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

    def store_document(self, 
                      content: str, 
                      metadata: Dict[str, Any], 
                      doc_type: str) -> str:
        """
        Store a document with its embeddings and metadata.
        
        Args:
            content (str): Document content
            metadata (Dict[str, Any]): Document metadata
            doc_type (str): Type of document (e.g., 'paper', 'repo', 'user')
            
        Returns:
            str: Document ID
        """
        try:
            # Generate embeddings
            embedding = self.embed_text(content)
            
            # Store embeddings
            embedding_doc = {
                'embedding': embedding,
                'doc_type': doc_type,
                'created_at': datetime.now()
            }
            embedding_id = self.embeddings_collection.insert_one(embedding_doc).inserted_id
            
            # Store metadata
            metadata_doc = {
                'embedding_id': embedding_id,
                'content': content,
                'metadata': metadata,
                'doc_type': doc_type,
                'created_at': datetime.now()
            }
            metadata_id = self.metadata_collection.insert_one(metadata_doc).inserted_id
            
            return str(metadata_id)
        except Exception as e:
            print(f"Error storing document: {e}")
            return ""

    def retrieve_similar_documents(self, 
                                 query: str, 
                                 doc_type: Optional[str] = None,
                                 limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve similar documents based on a query.
        
        Args:
            query (str): Query text
            doc_type (Optional[str]): Filter by document type
            limit (int): Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: List of similar documents with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embed_text(query)
            
            # Build aggregation pipeline
            pipeline = [
                {
                    "$vectorSearch": {
                        "queryVector": query_embedding,
                        "path": "embedding",
                        "numCandidates": 100,
                        "limit": limit,
                        "index": "vector_index"
                    }
                }
            ]
            
            if doc_type:
                pipeline.append({
                    "$match": {
                        "doc_type": doc_type
                    }
                })
            
            # Execute search
            results = list(self.embeddings_collection.aggregate(pipeline))
            
            # Get metadata for results
            similar_docs = []
            for result in results:
                metadata = self.metadata_collection.find_one({
                    'embedding_id': result['_id']
                })
                if metadata:
                    similar_docs.append({
                        'content': metadata['content'],
                        'metadata': metadata['metadata'],
                        'score': result.get('score', 0)
                    })
            
            return similar_docs
        except Exception as e:
            print(f"Error retrieving similar documents: {e}")
            return []

    def generate_with_context(self, context: str, query: str) -> str:
        """
        Generate text using Ollama with context.
        
        Args:
            context (str): The context to use for generation
            query (str): The query to answer
            
        Returns:
            str: Generated text
        """
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
                    {"role": "user", "content": query}
                ],
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()['message']['content']

    def create_twitter_post(self, content: str, style: str = "professional") -> Dict[str, Any]:
        """
        Create a Twitter post based on the content and style.
        
        Args:
            content (str): The main content to create a post about
            style (str): The style of the post (professional, casual, etc.)
            
        Returns:
            Dict[str, Any]: Generated Twitter post with metadata
        """
        # Create prompt for generating tweet
        prompt = f"""Generate a {style} tweet about this content:
        
        {content}
        
        IMPORTANT FORMATTING RULES:
        1. ABSOLUTELY NO EMOJIS OR SPECIAL CHARACTERS
        2. Use plain text only
        3. Maximum 230 characters
        4. Must be informative and technical but accessible
        5. Include key points
        6. Use hashtags sparingly (max 2-3)
        7. DO NOT include any URLs in the generated text"""
        
        # Generate tweet
        response = requests.post(
            f"{self.ollama_host}/api/chat",
            json={
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "You are a professional content creator."},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            }
        )
        response.raise_for_status()
        tweet = response.json()['message']['content']
        
        # Format response
        return {
            "content": tweet.strip(),
            "hashtags": ["#AI", "#Tech"],
            "mentions": [],
            "style": style,
            "character_count": len(tweet.strip())
        } 