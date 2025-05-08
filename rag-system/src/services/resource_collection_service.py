from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import requests
import json
import os
from dotenv import load_dotenv
from services.niche_analysis_service import NicheAnalysis
from dataclasses import dataclass

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class Resource:
    """Class representing a collected resource."""
    resource_id: str
    content: str
    metadata: Dict[str, Any]
    resource_type: str
    keywords: List[str]
    collected_at: datetime

class ResourceCollectionError(Exception):
    """Base class for ResourceCollectionService errors"""
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details

class ResourceCollectionService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.arxiv_api_url = "http://export.arxiv.org/api/query"
        self.github_api_url = "https://api.github.com/search/repositories"
        self._validate_config()

    def _validate_config(self):
        """Validate service configuration"""
        # For testing, we'll allow missing environment variables
        pass

    def collect_resources(self, analysis: NicheAnalysis, limit: int = 10) -> List[Resource]:
        """
        Collect resources based on niche analysis.
        
        Args:
            analysis: NicheAnalysis object containing topic and keywords
            limit: Maximum number of resources to collect per type
            
        Returns:
            List of Resource objects
        """
        self.logger.info(f"Collecting resources with analysis: {analysis}")
        
        resources = []
        
        # Mock academic papers
        self.logger.info("Collecting mock papers...")
        try:
            papers = self._mock_papers(analysis, limit)
            self.logger.info(f"Collected {len(papers)} papers")
            resources.extend(papers)
        except Exception as e:
            self.logger.error(f"Error collecting papers: {str(e)}", exc_info=True)
            # Continue with other resources
        
        # Mock GitHub repositories
        self.logger.info("Collecting mock repositories...")
        try:
            repos = self._mock_repositories(analysis, limit)
            self.logger.info(f"Collected {len(repos)} repositories")
            resources.extend(repos)
        except Exception as e:
            self.logger.error(f"Error collecting repositories: {str(e)}", exc_info=True)
            # Continue with other resources
        
        if not resources:
            self.logger.error("No resources were collected")
            raise ResourceCollectionError(
                "Failed to collect any resources",
                details={"analysis": str(analysis)}
            )
        
        self.logger.info(f"Total resources collected: {len(resources)}")
        return resources

    def _mock_papers(self, analysis: NicheAnalysis, limit: int) -> List[Resource]:
        """Generate mock academic papers."""
        papers = []
        for i in range(min(limit, 3)):
            paper = Resource(
                resource_id=f"paper_{i}",
                content=f"Research paper about {analysis.main_topic} focusing on {', '.join(analysis.keywords[:2])}. This paper discusses important aspects of the field.",
                metadata={
                    "title": f"Research on {analysis.main_topic}",
                    "authors": ["Author 1", "Author 2"],
                    "published": datetime.now().isoformat(),
                    "url": "https://arxiv.org/abs/mock",
                    "arxiv_id": f"mock_{i}",
                    "published_date": datetime.now().isoformat()
                },
                resource_type="paper",
                keywords=analysis.keywords,
                collected_at=datetime.now()
            )
            papers.append(paper)
        return papers

    def _mock_repositories(self, analysis: NicheAnalysis, limit: int) -> List[Resource]:
        """Generate mock GitHub repositories."""
        repos = []
        for i in range(min(limit, 3)):
            repo = Resource(
                resource_id=f"repo_{i}",
                content=f"Repository implementing {analysis.main_topic} with focus on {', '.join(analysis.keywords[:2])}. Includes examples and documentation.",
                metadata={
                    "repo_name": f"{analysis.main_topic}-implementation",
                    "owner": "mock-owner",
                    "url": "https://github.com/mock/repo",
                    "stars": 100,
                    "language": "Python"
                },
                resource_type="repository",
                keywords=analysis.keywords,
                collected_at=datetime.now()
            )
            repos.append(repo)
        return repos

    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """Retrieve a specific resource by ID."""
        try:
            # For testing, return a mock resource
            return Resource(
                resource_id=resource_id,
                content="Mock resource content for testing",
                metadata={
                    "title": "Mock Resource",
                    "source": "mock",
                    "url": "https://example.com"
                },
                resource_type="mock",
                keywords=["mock"],
                collected_at=datetime.now()
            )
        except Exception as e:
            self.logger.error(f"Error retrieving resource: {str(e)}", exc_info=True)
            raise ResourceCollectionError("Failed to retrieve resource", details=str(e))

    def update_resource(self, resource: Resource) -> Resource:
        """Update an existing resource."""
        try:
            # TODO: Implement actual database update
            # For now, just return the resource
            return resource
        except Exception as e:
            self.logger.error(f"Error updating resource: {str(e)}", exc_info=True)
            raise ResourceCollectionError("Failed to update resource", details=str(e))

    def delete_resource(self, resource_id: str) -> bool:
        """Delete a resource."""
        try:
            # TODO: Implement actual database deletion
            # For now, return True
            return True
        except Exception as e:
            self.logger.error(f"Error deleting resource: {str(e)}", exc_info=True)
            raise ResourceCollectionError("Failed to delete resource", details=str(e)) 