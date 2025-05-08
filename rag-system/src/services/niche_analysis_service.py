from typing import Dict, List, Any
import logging
from dataclasses import dataclass
from datetime import datetime
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class NicheAnalysisError(Exception):
    """Base class for NicheAnalysisService errors"""
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details

class OllamaError(NicheAnalysisError):
    """Raised when Ollama API calls fail"""
    pass

class ValidationError(NicheAnalysisError):
    """Raised when input validation fails"""
    pass

@dataclass
class NicheAnalysis:
    main_topic: str
    subtopics: List[str]
    keywords: List[str]
    content_style: str
    target_platforms: List[str]
    generated_at: datetime

class NicheAnalysisService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.model_name = os.getenv('MODEL_NAME', 'gemma:7b')
        self._validate_config()

    def _validate_config(self):
        """Validate service configuration"""
        if not self.ollama_host:
            raise ValidationError("OLLAMA_HOST environment variable is not set")
        if not self.model_name:
            raise ValidationError("MODEL_NAME environment variable is not set")

    def _validate_user_input(self, user_input: Dict[str, Any]):
        """Validate user input structure"""
        self.logger.info(f"Validating user input: {user_input}")
        self.logger.info(f"User input type: {type(user_input)}")
        
        # Ensure input is a dictionary
        if not isinstance(user_input, dict):
            self.logger.error(f"Invalid input type: {type(user_input)}")
            raise ValidationError("User input must be a dictionary")
        
        # Ensure topic exists and is not empty
        if not user_input.get('topic'):
            self.logger.error("Missing topic in user input")
            raise ValidationError("Topic is required in user input")
        
        # Ensure preferences exist and is a dictionary
        if 'preferences' not in user_input:
            user_input['preferences'] = {}
        elif not isinstance(user_input['preferences'], dict):
            self.logger.error(f"Invalid preferences type: {type(user_input['preferences'])}")
            raise ValidationError("Preferences must be a dictionary")
        
        # Ensure all required fields in preferences are present
        if 'platform' not in user_input['preferences']:
            user_input['preferences']['platform'] = 'twitter'
        if 'style' not in user_input['preferences']:
            user_input['preferences']['style'] = 'professional'
        if 'query_context' not in user_input['preferences']:
            user_input['preferences']['query_context'] = user_input.get('topic', '')
        
        # Log validation results
        self.logger.info(f"Validated user input: {user_input}")
        self.logger.info(f"Validated user input type: {type(user_input)}")
        self.logger.info(f"Validated user input keys: {user_input.keys()}")
        self.logger.info(f"Validated preferences: {user_input['preferences']}")
        self.logger.info(f"Validated preferences type: {type(user_input['preferences'])}")
        
        return user_input

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API with the given prompt."""
        try:
            response = requests.post(
                f"{self.ollama_host}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False
                },
                timeout=30  # 30 second timeout
            )
            response.raise_for_status()
            result = response.json()
            if 'message' in result:
                return result['message']['content']
            return result.get('response', '')
        except requests.exceptions.Timeout:
            raise OllamaError("Ollama API request timed out")
        except requests.exceptions.ConnectionError:
            raise OllamaError("Failed to connect to Ollama service")
        except requests.exceptions.RequestException as e:
            raise OllamaError(f"Ollama API request failed: {str(e)}")
        except (KeyError, json.JSONDecodeError) as e:
            raise OllamaError(f"Invalid response from Ollama: {str(e)}")

    def _extract_main_topic(self, user_input: Dict[str, Any]) -> str:
        """Extract the main topic from user input using LLM."""
        try:
            prompt = f"""
            Analyze the following user input and extract the main topic. 
            Return only the main topic, nothing else.
            
            User Input: {user_input.get('topic', '')}
            Preferences: {user_input.get('preferences', {})}
            """
            topic = self._call_ollama(prompt).strip()
            if not topic:
                raise ValidationError("Failed to extract main topic")
            return topic
        except Exception as e:
            raise NicheAnalysisError("Failed to extract main topic", details=str(e))

    def _generate_subtopics(self, main_topic: str) -> List[str]:
        """Generate relevant subtopics for the main topic using LLM."""
        try:
            prompt = f"""
            Generate 3-5 relevant subtopics for the main topic: {main_topic}
            Return the subtopics as a JSON array of strings.
            """
            response = self._call_ollama(prompt)
            try:
                subtopics = json.loads(response)
                if not isinstance(subtopics, list) or len(subtopics) < 3:
                    raise ValidationError("Invalid subtopics format")
                return subtopics
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                subtopics = [line.strip() for line in response.split('\n') if line.strip()]
                if len(subtopics) < 3:
                    raise ValidationError("Insufficient subtopics generated")
                return subtopics
        except Exception as e:
            raise NicheAnalysisError("Failed to generate subtopics", details=str(e))

    def _generate_keywords(self, main_topic: str, subtopics: List[str]) -> List[str]:
        """Generate SEO keywords based on topic and subtopics using LLM."""
        try:
            prompt = f"""
            Generate 5-10 SEO keywords for the following topic and subtopics.
            Return the keywords as a JSON array of strings.
            
            Main Topic: {main_topic}
            Subtopics: {', '.join(subtopics)}
            """
            response = self._call_ollama(prompt)
            try:
                keywords = json.loads(response)
                if not isinstance(keywords, list) or len(keywords) < 5:
                    raise ValidationError("Invalid keywords format")
                return keywords
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                keywords = [line.strip() for line in response.split('\n') if line.strip()]
                if len(keywords) < 5:
                    raise ValidationError("Insufficient keywords generated")
                return keywords
        except Exception as e:
            raise NicheAnalysisError("Failed to generate keywords", details=str(e))

    def _determine_content_style(self, user_input: Dict[str, Any]) -> str:
        """Determine the appropriate content style using LLM."""
        try:
            prompt = f"""
            Analyze the following user preferences and determine the most appropriate content style.
            Choose from: professional, casual, technical, academic, or conversational.
            Return only the style, nothing else.
            
            Preferences: {user_input.get('preferences', {})}
            """
            style = self._call_ollama(prompt).strip().lower()
            valid_styles = ['professional', 'casual', 'technical', 'academic', 'conversational']
            if style not in valid_styles:
                raise ValidationError(f"Invalid content style: {style}")
            return style
        except Exception as e:
            raise NicheAnalysisError("Failed to determine content style", details=str(e))

    def _get_target_platforms(self, user_input: Dict[str, Any]) -> List[str]:
        """Get target platforms from user input using LLM."""
        try:
            prompt = f"""
            Analyze the following user preferences and determine the most appropriate platforms.
            Choose from: twitter, linkedin, medium, github.
            Return the platforms as a JSON array of strings.
            
            Preferences: {user_input.get('preferences', {})}
            """
            response = self._call_ollama(prompt)
            try:
                platforms = json.loads(response)
                valid_platforms = ['twitter', 'linkedin', 'medium', 'github']
                platforms = [p for p in platforms if p in valid_platforms]
                if not platforms:
                    raise ValidationError("No valid platforms selected")
                return platforms
            except json.JSONDecodeError:
                return ['twitter']  # Default to Twitter if parsing fails
        except Exception as e:
            raise NicheAnalysisError("Failed to determine target platforms", details=str(e))

    def analyze_niche(self, user_input: Dict[str, Any]) -> NicheAnalysis:
        """
        Analyze user input to determine niche, topics, and content requirements.
        
        Args:
            user_input: Dictionary containing user preferences and requirements
            
        Returns:
            NicheAnalysis object containing analyzed information
            
        Raises:
            ValidationError: If input validation fails
            NicheAnalysisError: If analysis fails
        """
        try:
            self.logger.info("Starting niche analysis")
            self.logger.info(f"Input type: {type(user_input)}")
            self.logger.info(f"Input content: {user_input}")
            
            # Validate input
            self._validate_user_input(user_input)
            
            # Extract main topic
            main_topic = self._extract_main_topic(user_input)
            self.logger.info(f"Main topic: {main_topic}")
            
            # Generate subtopics
            subtopics = self._generate_subtopics(main_topic)
            self.logger.info(f"Generated subtopics: {subtopics}")
            
            # Generate keywords
            keywords = self._generate_keywords(main_topic, subtopics)
            self.logger.info(f"Generated keywords: {keywords}")
            
            # Determine content style
            content_style = self._determine_content_style(user_input)
            self.logger.info(f"Content style: {content_style}")
            
            # Get target platforms
            target_platforms = self._get_target_platforms(user_input)
            self.logger.info(f"Target platforms: {target_platforms}")
            
            # Create and return analysis
            analysis = NicheAnalysis(
                main_topic=main_topic,
                subtopics=subtopics,
                keywords=keywords,
                content_style=content_style,
                target_platforms=target_platforms,
                generated_at=datetime.now()
            )
            self.logger.info(f"Analysis completed: {analysis}")
            return analysis
            
        except ValidationError as e:
            self.logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Analysis error: {str(e)}")
            raise NicheAnalysisError(f"Failed to analyze niche: {str(e)}")

    def update_analysis(self, analysis: NicheAnalysis, new_data: Dict[str, Any]) -> NicheAnalysis:
        """
        Update existing niche analysis with new data.
        
        Args:
            analysis: Existing NicheAnalysis object
            new_data: New data to incorporate
            
        Returns:
            Updated NicheAnalysis object
            
        Raises:
            ValidationError: If input validation fails
            NicheAnalysisError: If update fails
        """
        try:
            # Validate input
            self._validate_user_input(new_data)
            
            # Update main topic if provided
            if 'topic' in new_data:
                analysis.main_topic = self._extract_main_topic(new_data)
                analysis.subtopics = self._generate_subtopics(analysis.main_topic)
                analysis.keywords = self._generate_keywords(analysis.main_topic, analysis.subtopics)
            
            # Update content style if provided
            if 'style' in new_data:
                analysis.content_style = self._determine_content_style(new_data)
            
            # Update platforms if provided
            if 'platforms' in new_data:
                analysis.target_platforms = self._get_target_platforms(new_data)
            
            return analysis
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Error updating niche analysis: {str(e)}", exc_info=True)
            raise NicheAnalysisError("Failed to update niche analysis", details=str(e)) 