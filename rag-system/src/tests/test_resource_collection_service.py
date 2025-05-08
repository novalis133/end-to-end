import unittest
from datetime import datetime
from services.resource_collection_service import ResourceCollectionService, Resource
from services.niche_analysis_service import NicheAnalysis
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TestResourceCollectionService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.service = ResourceCollectionService()
        self.test_analysis = NicheAnalysis(
            main_topic="Large Language Models",
            subtopics=["transformer architecture", "attention mechanisms"],
            keywords=["llm", "transformer", "attention", "neural networks"],
            content_style="professional",
            target_platforms=["twitter"],
            generated_at=datetime.now()
        )

    def test_collect_resources(self):
        """Test collecting resources based on niche analysis."""
        try:
            resources = self.service.collect_resources(
                analysis=self.test_analysis,
                limit=5
            )
            
            # Verify resources were collected
            self.assertIsInstance(resources, list)
            self.assertTrue(len(resources) > 0)
            
            # Verify resource structure
            for resource in resources:
                self.assertIsInstance(resource, Resource)
                self.assertIsInstance(resource.resource_id, str)
                self.assertIsInstance(resource.content, str)
                self.assertIsInstance(resource.metadata, dict)
                self.assertIsInstance(resource.resource_type, str)
                self.assertIsInstance(resource.keywords, list)
                self.assertIsInstance(resource.collected_at, datetime)
                
                # Verify metadata fields
                self.assertIn('title', resource.metadata)
                self.assertIn('source', resource.metadata)
                self.assertIn('url', resource.metadata)
                
        except Exception as e:
            self.fail(f"Failed to collect resources: {str(e)}")

    def test_get_resource(self):
        """Test retrieving a specific resource."""
        # First collect some resources
        resources = self.service.collect_resources(
            analysis=self.test_analysis,
            limit=1
        )
        
        if resources:
            resource_id = resources[0].resource_id
            
            # Try to retrieve the resource
            retrieved_resource = self.service.get_resource(resource_id)
            
            # Verify the retrieved resource
            self.assertIsInstance(retrieved_resource, Resource)
            self.assertEqual(retrieved_resource.resource_id, resource_id)
            self.assertEqual(retrieved_resource.content, resources[0].content)
            self.assertEqual(retrieved_resource.metadata, resources[0].metadata)
            self.assertEqual(retrieved_resource.resource_type, resources[0].resource_type)
            self.assertEqual(retrieved_resource.keywords, resources[0].keywords)

    def test_collect_papers(self):
        """Test collecting academic papers."""
        try:
            papers = self.service._collect_papers(
                main_topic=self.test_analysis.main_topic,
                keywords=self.test_analysis.keywords,
                limit=3
            )
            
            # Verify papers were collected
            self.assertIsInstance(papers, list)
            self.assertTrue(len(papers) > 0)
            
            # Verify paper structure
            for paper in papers:
                self.assertIsInstance(paper, Resource)
                self.assertEqual(paper.resource_type, "paper")
                self.assertIn('arxiv_id', paper.metadata)
                self.assertIn('authors', paper.metadata)
                self.assertIn('published_date', paper.metadata)
                
        except Exception as e:
            self.fail(f"Failed to collect papers: {str(e)}")

    def test_collect_repositories(self):
        """Test collecting GitHub repositories."""
        try:
            repos = self.service._collect_repositories(
                main_topic=self.test_analysis.main_topic,
                keywords=self.test_analysis.keywords,
                limit=3
            )
            
            # Verify repositories were collected
            self.assertIsInstance(repos, list)
            self.assertTrue(len(repos) > 0)
            
            # Verify repository structure
            for repo in repos:
                self.assertIsInstance(repo, Resource)
                self.assertEqual(repo.resource_type, "repository")
                self.assertIn('repo_name', repo.metadata)
                self.assertIn('owner', repo.metadata)
                self.assertIn('stars', repo.metadata)
                self.assertIn('language', repo.metadata)
                
        except Exception as e:
            self.fail(f"Failed to collect repositories: {str(e)}")

    def test_invalid_resource_id(self):
        """Test retrieving a non-existent resource."""
        retrieved_resource = self.service.get_resource("invalid_id")
        self.assertIsNone(retrieved_resource)

    def test_empty_keywords(self):
        """Test collecting resources with empty keywords."""
        empty_analysis = NicheAnalysis(
            main_topic="Large Language Models",
            subtopics=[],
            keywords=[],
            content_style="professional",
            target_platforms=["twitter"],
            generated_at=datetime.now()
        )
        
        with self.assertRaises(Exception):
            self.service.collect_resources(
                analysis=empty_analysis,
                limit=5
            )

if __name__ == '__main__':
    unittest.main() 