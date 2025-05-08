from typing import Dict, Any, List
import logging
from datetime import datetime
from .niche_analysis_service import NicheAnalysisService, NicheAnalysis
from .resource_collection_service import ResourceCollectionService
from .rag_service import RAGService
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PipelineService:
    def __init__(self):
        self.niche_service = NicheAnalysisService()
        self.resource_service = ResourceCollectionService()
        self.rag_service = RAGService()
        
    def process_content_request(self, account_id: str, topic: str, query: str, platform: str = "twitter", content_style: str = "professional") -> Dict[str, Any]:
        """
        Process a content generation request through the full pipeline.
        
        Args:
            account_id: The account ID
            topic: The main topic
            query: The specific query for content generation
            platform: The target platform (default: twitter)
            content_style: The content style (default: professional)
            
        Returns:
            Dict containing the generated content and metadata
        """
        try:
            logger.info(f"Starting content request processing with inputs: account_id={account_id}, topic={topic}, query={query}, platform={platform}, content_style={content_style}")
            
            # Step 1: Store account if not exists
            try:
                self.rag_service.store_account(account_id)
                logger.info(f"Account {account_id} stored successfully")
            except Exception as e:
                logger.warning(f"Failed to store account: {str(e)}")
            
            # Step 2: Analyze niche and store preferences
            logger.info(f"Analyzing niche for account {account_id}")
            
            # Format input for niche analysis
            niche_input = {
                'topic': topic,
                'preferences': {
                    'platform': platform,
                    'style': content_style,
                    'query_context': query
                }
            }
            
            logger.info(f"Niche input type: {type(niche_input)}")
            logger.info(f"Niche input content: {niche_input}")
            
            try:
                logger.info("Calling analyze_niche with input")
                analysis: NicheAnalysis = self.niche_service.analyze_niche(niche_input)
                logger.info("Niche analysis completed successfully")
            except Exception as e:
                logger.error(f"Niche analysis failed with input {niche_input}: {str(e)}", exc_info=True)
                # Create a simple analysis without LLM
                analysis = NicheAnalysis(
                    main_topic=topic,
                    subtopics=[topic],
                    keywords=[topic.lower()],
                    content_style='professional',
                    target_platforms=[platform],
                    generated_at=datetime.now()
                )
                logger.info("Created fallback analysis")
            
            # Step 3: Store preferences
            try:
                preferences_data = {
                    'niche': analysis.main_topic,
                    'subtopics': analysis.subtopics,
                    'keywords': analysis.keywords,
                    'style': analysis.content_style,
                    'platforms': analysis.target_platforms
                }
                logger.info(f"Storing preferences: {preferences_data}")
                preference_id = self.rag_service.store_preferences(
                    account_id=account_id,
                    preferences=preferences_data
                )
                logger.info(f"Preferences stored with ID: {preference_id}")
            except Exception as e:
                logger.error(f"Failed to store preferences: {str(e)}", exc_info=True)
                preference_id = f"error_{datetime.now().timestamp()}"
            
            # Step 4: Generate content
            logger.info(f"Generating content for account {account_id}")
            try:
                if platform == "twitter":
                    logger.info(f"Generating Twitter post with style: {analysis.content_style}")
                    result = self.rag_service.create_twitter_post(
                        content=query,
                        style=analysis.content_style
                    )
                    content = result.get('content', query)
                else:
                    logger.info(f"Generating content for platform: {platform}")
                    content = self.rag_service.generate_with_context(
                        context=query,
                        query=query
                    )
                logger.info("Content generated successfully")
            except Exception as e:
                logger.error(f"Content generation failed: {str(e)}", exc_info=True)
                # Use a simple content generation fallback
                content = f"Here's what you need to know about {topic}: {query}"
                logger.info("Created fallback content")
            
            # Step 5: Store the post
            try:
                post_metadata = {
                    'preference_id': preference_id,
                    'style': analysis.content_style,
                    'generated_at': datetime.now().isoformat(),
                    'platform_specific': {
                        'character_count': len(content)
                    }
                }
                logger.info(f"Storing post with metadata: {post_metadata}")
                post_id = self.rag_service.store_post(
                    account_id=account_id,
                    resource_id=None,  # No resource for now
                    content=content,
                    platform=platform,
                    metadata=post_metadata
                )
                logger.info(f"Post stored with ID: {post_id}")
            except Exception as e:
                logger.error(f"Failed to store post: {str(e)}", exc_info=True)
                post_id = f"error_{datetime.now().timestamp()}"
            
            result = {
                "account_id": account_id,
                "post_id": post_id,
                "content": content,
                "platform": platform,
                "generated_at": datetime.now().isoformat(),
                "performance_metrics": {
                    "views": 0,
                    "likes": 0,
                    "shares": 0,
                    "comments": 0
                }
            }
            logger.info(f"Returning result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in pipeline processing: {str(e)}", exc_info=True)
            raise Exception(f"Pipeline processing failed: {str(e)}") 