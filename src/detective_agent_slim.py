#!/usr/bin/env python3
"""
Detective Agent Slim - Simplified entry point for the Narrahunt investigation system

This slim version of the detective agent is used by integrated_main.py.
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import core functionality from modules
from modules.agent_core import start_investigation, execute_investigation
from modules.routing import review_research_strategy, extract_leads_from_discovery
from modules.extractors import extract_artifacts_from_html, extract_names_from_text
from modules.llm_engine import get_llm_instance, alternate_llm_instance

class DetectiveAgent:
    """
    Simplified detective agent class for integration with other systems.
    """
    
    def __init__(self, objective: str, entity: str, max_iterations: int = 50,
                 max_idle_iterations: int = 10, save_path: Optional[str] = None):
        """
        Initialize the detective agent.
        
        Args:
            objective: The research objective
            entity: The primary entity to investigate
            max_iterations: Maximum number of investigation iterations
            max_idle_iterations: Maximum consecutive iterations without new discoveries
            save_path: Path to save discoveries and state
        """
        self.objective = objective
        self.entity = entity
        self.max_iterations = max_iterations
        self.max_idle_iterations = max_idle_iterations
        self.save_path = save_path or os.path.join(os.getcwd(), "discoveries")
        
        # Ensure save directory exists
        os.makedirs(self.save_path, exist_ok=True)
        
        # Initialize state
        self.current_iteration = 0
        self.idle_iterations = 0
        self.discoveries = []
        self.iteration_discoveries = {}
        self.current_target = None
        self.llm_calls_count = 0
        
        # Initialize research strategy
        self.research_strategy = None
        
        logger.info(f"Detective Agent initialized with objective: {objective}")
        logger.info(f"Primary entity: {entity}")
        
    def start_investigation(self):
        """Start the investigation process."""
        # Call the modularized start_investigation function
        return start_investigation(self)
    
    def _get_llm_instance(self):
        """Get an LLM instance, alternating between providers."""
        return alternate_llm_instance(self.llm_calls_count)
        
    def _extract_urls_from_text(self, text):
        """Extract URLs from text."""
        import re
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        return re.findall(url_pattern, text)
        
    def _is_url_relevant(self, url):
        """Check if a URL is relevant to the investigation."""
        # Simple relevance check - avoid media files, etc.
        irrelevant_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.mp3', '.mp4']
        return not any(url.lower().endswith(ext) for ext in irrelevant_extensions)
        
    def _should_check_wayback(self, url):
        """Check if we should look up this URL in Wayback Machine."""
        # Only check main pages and important domains
        parsed_url = urlparse(url) if 'urlparse' in globals() else None
        if not parsed_url:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            
        path = parsed_url.path
        return path == '' or path == '/' or len(path.split('/')) <= 2