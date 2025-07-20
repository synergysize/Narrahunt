#!/usr/bin/env python3
"""
LLM Research Strategy Generator

This module uses an LLM to generate research strategies based on narrative objectives.
It converts high-level objectives into specific, crawlable URLs and search queries.
"""

import os
import re
import json
import logging
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from datetime import datetime
from dotenv import load_dotenv
from config_loader import get_api_key

# Configure logging
base_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(base_dir, 'logs'), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(base_dir, 'logs', 'llm_strategy.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('llm_research_strategy')

class LLMResearchStrategy:
    """
    Uses LLM to generate research strategies for narrative objectives.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM Research Strategy generator.
        
        Args:
            api_key: Optional API key for the LLM service
            
        Raises:
            ValueError: If no API key is provided or found in environment
        """
        # Load environment variables
        load_dotenv()
        
        # Try to get the API key in order of precedence:
        # 1. Explicitly provided api_key parameter
        # 2. CLAUDE_API_KEY from environment (via config_loader)
        # 3. LLM_API_KEY from environment (legacy)
        self.api_key = api_key or get_api_key('CLAUDE_API_KEY') or os.environ.get('LLM_API_KEY')
        
        if not self.api_key:
            raise ValueError("No LLM API key provided. Please set CLAUDE_API_KEY in your .env file.")
        
        # Load strategy templates
        self.strategy_templates_path = os.path.join(base_dir, 'config', 'strategy_templates.json')
        self.strategy_templates = self._load_strategy_templates()
        
        # Track generated strategies for caching
        self.strategy_cache = {}
    
    def _load_strategy_templates(self) -> Dict[str, Any]:
        """Load strategy templates from file or create default ones."""
        if os.path.exists(self.strategy_templates_path):
            try:
                with open(self.strategy_templates_path, 'r') as f:
                    return json.load(f)
            except:
                logger.error(f"Error loading strategy templates from {self.strategy_templates_path}")
        
        # Default strategy templates
        default_templates = {
            "name": {
                "prompt": "I'm researching historical names, usernames, project names, or terminology associated with {entity} before their current projects became well-known. What specific sources should I check? What specific search queries should I use? What GitHub repositories, forum usernames, or early blog posts might contain this information?",
                "sources": [
                    "github.com/{username}",
                    "twitter.com/{twitter_handle}",
                    "{blog_url}",
                    "reddit.com/user/{reddit_username}",
                    "forum.{community}.org/user/{forum_username}",
                    "archive.org/web/*/vitalik.ca/*"
                ],
                "search_queries": [
                    "{entity} username before {year}",
                    "{entity} early projects",
                    "{entity} early forum posts",
                    "{entity} before {current_project}",
                    "{entity} old blog",
                    "{entity} previously known as"
                ]
            },
            "wallet": {
                "prompt": "I'm researching cryptocurrency wallets, addresses, or transactions associated with {entity}. What specific sources should I check for information about their early transactions, wallet addresses, or donation addresses? What specific search queries would help me find this information?",
                "sources": [
                    "etherscan.io/address/{known_address}",
                    "github.com/{username}",
                    "{blog_url}/donate",
                    "twitter.com/{twitter_handle}",
                    "blockchain.com/explorer"
                ],
                "search_queries": [
                    "{entity} ethereum address",
                    "{entity} donation address",
                    "{entity} wallet address",
                    "{entity} crypto transactions",
                    "{entity} early ethereum",
                    "{entity} eth address github"
                ]
            },
            "code": {
                "prompt": "I'm researching code, repositories, or programming projects associated with {entity} during their early career. What specific GitHub repositories, gists, or code-related sources should I check? What specific search queries would help me find their early code contributions?",
                "sources": [
                    "github.com/{username}",
                    "github.com/{username}?tab=repositories&type=source&sort=created_asc",
                    "gist.github.com/{username}",
                    "gitlab.com/{username}",
                    "stackoverflow.com/users/{so_username}"
                ],
                "search_queries": [
                    "{entity} github first repository",
                    "{entity} early code contributions",
                    "{entity} first commit",
                    "{entity} code before {current_project}",
                    "site:github.com {entity} created:2013-01-01..2016-01-01",
                    "{entity} programming language"
                ]
            },
            "personal": {
                "prompt": "I'm researching personal information, biographical details, or relationships associated with {entity} during their early career. What specific sources should I check for information about their education, early employment, or personal connections? What specific search queries would help me find this information?",
                "sources": [
                    "linkedin.com/in/{linkedin_username}",
                    "{blog_url}/about",
                    "twitter.com/{twitter_handle}",
                    "medium.com/@{medium_username}",
                    "archive.org/web/*/{personal_website}/*"
                ],
                "search_queries": [
                    "{entity} biography",
                    "{entity} education",
                    "{entity} early career",
                    "{entity} interview",
                    "{entity} background",
                    "{entity} hometown",
                    "{entity} family",
                    "{entity} university"
                ]
            }
        }
        
        # Save default templates
        os.makedirs(os.path.dirname(self.strategy_templates_path), exist_ok=True)
        with open(self.strategy_templates_path, 'w') as f:
            json.dump(default_templates, f, indent=2)
        
        return default_templates
    
    def _call_llm_api(self, prompt: str) -> str:
        """
        Call the LLM API to generate a research strategy.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The LLM's response text
        """
        # Try to import the LLM integration module
        try:
            from llm_integration import LLMIntegration
            llm = LLMIntegration(use_claude=True, use_openai=False)
            logger.info("Using real LLM integration with Claude API")
            
            # Using Claude to analyze the prompt directly
            # Extract the entity from the prompt
            import re
            entity_match = re.search(r'associated with ([^\.]+)', prompt)
            entity = entity_match.group(1) if entity_match else "the subject"
            
            # Generate a research strategy
            strategy = llm.generate_research_strategy(prompt, entity)
            
            # Convert the strategy to a string response
            import json
            return json.dumps(strategy)
            
        except ImportError:
            logger.warning("LLM integration module not found. Using simulated response.")
            return self._generate_simulated_response(prompt)
        except Exception as e:
            logger.error(f"Error calling LLM API: {e}")
            return self._generate_simulated_response(prompt)
    
    def _generate_simulated_response(self, prompt: str) -> str:
        """
        Generate a simulated LLM response for testing.
        
        Args:
            prompt: The input prompt
            
        Returns:
            A simulated response text
        """
        # Extract entity from prompt
        entity_match = re.search(r'associated with ([^\.]+)', prompt)
        entity = entity_match.group(1) if entity_match else "the subject"
        
        # Check what type of artifact we're researching
        if "names, usernames, project names" in prompt:
            return f"""
To research historical names, usernames, project names, or terminology associated with {entity}, I recommend the following approach:

Specific Sources to Check:
1. GitHub Profile: github.com/vbuterin - Check early repositories, commits, and contributions
2. Early Blog: vitalik.ca - Especially posts from 2013-2015
3. Bitcoin Forum: bitcointalk.org/index.php?action=profile;u=11772 - Where Vitalik was active before Ethereum
4. Ethereum Research Forum: ethresear.ch/u/vitalik/activity
5. Reddit: reddit.com/user/vbuterin - Check oldest posts
6. Twitter: twitter.com/VitalikButerin - Look at earliest tweets
7. Internet Archive: web.archive.org/web/*/vitalik.ca/* - For historical snapshots
8. Ethereum GitHub: github.com/ethereum - Check earliest contributors
9. Bitcoin Magazine: bitcoinmagazine.com/authors/vitalik-buterin - His early articles

Search Queries:
1. "Vitalik Buterin username bitcointalk"
2. "Vitalik Buterin before Ethereum"
3. "Vitalik Buterin Bitcoin Magazine"
4. "Early Ethereum project name"
5. "Vitalik Buterin Colored Coins"
6. "Vitalik Buterin username 2013"
7. "Vitalik Buterin early projects GitHub"
8. "Vitalik Buterin pseudonym"
9. "Ethereum early codename"
10. "Vitalik Buterin Python projects before Ethereum"

GitHub Repositories:
1. github.com/vbuterin/pybitcointools - Early Bitcoin project
2. github.com/ethereum/wiki - Check earliest wiki edits
3. github.com/ethereum/EIPs - Early Ethereum Improvement Proposals

Forum Usernames:
1. vitalik_buterin
2. v_buterin
3. vitalik on ethresear.ch

Early Blog Posts:
1. vitalik.ca/general/2017/ - Check for references to earlier work
2. vitalik.ca/general/2013/ - If available through Internet Archive
3. bitcoinmagazine.com's earliest articles by Vitalik
"""
        elif "wallet" in prompt:
            return f"""
To research cryptocurrency wallets, addresses, or transactions associated with {entity}, I recommend the following approach:

Specific Sources to Check:
1. Ethereum Blockchain Explorer: etherscan.io - Search for known addresses
2. Vitalik's Blog: vitalik.ca - Check for donation addresses
3. Ethereum Foundation Website: ethereum.org - Look for foundation wallet addresses
4. GitHub Repositories: github.com/vbuterin and github.com/ethereum - May contain test addresses in code
5. Early ICO Documentation: If available, for Ethereum's initial coin offering
6. Ethereum Foundation Transparency Reports: May list official addresses
7. ENS Domain Records: Check for vitalik.eth and related domains
8. Web Archive: web.archive.org for historical versions of sites with addresses

Known Addresses to Check:
1. 0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B - Known Vitalik address
2. 0x1Db3439a222C519ab44bb1144fC28167b4Fa6EE6 - Another verified address

Search Queries:
1. "Vitalik Buterin ethereum address"
2. "Vitalik Buterin donation address"
3. "Ethereum Foundation wallet address"
4. "Vitalik.eth address"
5. "Vitalik Buterin crypto holdings"
6. "Ethereum genesis block Vitalik address"
7. "Vitalik Buterin ETH transactions"
8. "Vitalik Buterin verified addresses"

GitHub Specific:
1. Search for wallet patterns in vbuterin repositories
2. Check early Ethereum test scripts for addresses
3. Look for genesis block allocation code with addresses
"""
        elif "code" in prompt:
            return f"""
To research code, repositories, or programming projects associated with {entity} during their early career, I recommend the following approach:

Specific GitHub Repositories:
1. github.com/vbuterin/pybitcointools - Early Bitcoin-related Python library
2. github.com/vbuterin/cryptolife - May contain personal cryptography projects
3. github.com/ethereum/go-ethereum - Earliest commits to Ethereum's Go implementation
4. github.com/ethereum/cpp-ethereum - Early C++ implementation
5. github.com/ethereum/yellowpaper - The Ethereum Yellow Paper repository
6. github.com/ethereum/EIPs - Ethereum Improvement Proposals
7. github.com/ethereum/solidity - Early versions of Solidity language
8. github.com/ethereum/mist - The original Ethereum wallet interface

Historical GitHub URLs:
1. github.com/vbuterin?tab=repositories&type=source&sort=created_asc - Oldest repositories first
2. github.com/vbuterin?tab=activity&from=2013-01-01&to=2015-12-31 - Activity during early years
3. github.com/ethereum?page=15 - Navigate to oldest repositories

Search Queries:
1. "site:github.com vitalik buterin created:2010-01-01..2014-01-01" - Pre-Ethereum code
2. "vitalik buterin python projects before ethereum"
3. "vitalik buterin first github repository"
4. "vitalik buterin code contributions bitcoin"
5. "vitalik buterin colored coins implementation"
6. "ethereum earliest commit vitalik"
7. "vitalik buterin programming languages"
8. "ethereum proof of concept vitalik code"

Code-Related Sources:
1. gist.github.com/vbuterin - Check for early code snippets
2. stackoverflow.com/users/[userid] - If Vitalik has a Stack Overflow account
3. ethresear.ch - Research forum with code discussions
4. bitcointalk.org threads where Vitalik shared early code
5. ethereum.org/whitepaper - Original whitepaper with code concepts
6. web.archive.org for historical versions of GitHub repositories
"""
        else:
            return f"""
To research information associated with {entity}, I recommend checking the following sources:

1. Personal website: vitalik.ca - Especially the earliest blog posts
2. GitHub: github.com/vbuterin - Look at oldest repositories and commits
3. Twitter: twitter.com/VitalikButerin - Earliest tweets may contain valuable information
4. Internet Archive: web.archive.org to look at historical versions of their websites
5. Forum posts: bitcointalk.org where many early crypto developers were active
6. Academic papers: scholar.google.com search for early papers
7. YouTube: Early interviews and presentations
8. GitHub gists: gist.github.com for code snippets
9. Reddit: reddit.com/user/vbuterin for community engagement

Search Queries:
1. "{entity} early career"
2. "{entity} before 2015"
3. "{entity} first project"
4. "{entity} early interviews"
5. "{entity} university work"
6. "{entity} dissertation OR thesis"
7. "{entity} early collaborators"
8. "site:github.com {entity} created:2010-01-01..2014-01-01"
"""
    
    def generate_research_strategy(self, objective: str, entity: str) -> Dict[str, Any]:
        """
        Generate a research strategy for a given objective and entity.
        
        Args:
            objective: The research objective
            entity: The target entity
            
        Returns:
            A dictionary containing research strategy details
        """
        # Check cache first
        cache_key = f"{objective}:{entity}"
        if cache_key in self.strategy_cache:
            logger.info(f"Using cached strategy for {objective} about {entity}")
            return self.strategy_cache[cache_key]
        
        # Determine the artifact type from the objective
        artifact_type = None
        for potential_type in ["name", "wallet", "code", "personal", "legal", "academic", "hidden", "institutional"]:
            if potential_type in objective.lower():
                artifact_type = potential_type
                break
        
        if not artifact_type:
            artifact_type = "general"
            logger.warning(f"Could not determine artifact type from objective: {objective}")
        
        # Get the template for this artifact type
        template = self.strategy_templates.get(artifact_type, {})
        
        # Generate the prompt
        if "prompt" in template:
            prompt = template["prompt"].format(entity=entity, current_project="Ethereum", year="2015")
        else:
            prompt = f"I'm researching information associated with {entity}. What specific sources should I check? What specific search queries would help me find information about their early career, projects, or contributions?"
        
        # Get LLM response
        llm_response = self._call_llm_api(prompt)
        
        # Extract specific information from the LLM response
        sources = []
        search_queries = []
        github_repos = []
        usernames = []
        
        # Extract sources
        source_lines = re.findall(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9][-a-zA-Z0-9]*(?:\.[a-zA-Z0-9][-a-zA-Z0-9]*)+)(?:/[^\s]*)?', llm_response)
        sources.extend([f"https://{source}" if not source.startswith(('http://', 'https://')) else source for source in source_lines])
        
        # Extract search queries - lines that are in quotes
        search_query_lines = re.findall(r'"([^"]+)"', llm_response)
        search_queries.extend(search_query_lines)
        
        # Extract GitHub repos
        github_repos_lines = re.findall(r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+)', llm_response)
        github_repos.extend([f"https://github.com/{repo}" for repo in github_repos_lines])
        
        # Extract usernames
        username_lines = re.findall(r'@([a-zA-Z0-9_-]+)', llm_response)
        usernames.extend(username_lines)
        
        # Get template sources and search queries
        if "sources" in template:
            template_sources = [
                source.format(
                    username="vbuterin", 
                    twitter_handle="VitalikButerin",
                    blog_url="vitalik.ca",
                    reddit_username="vbuterin",
                    forum_username="vitalik",
                    community="ethereum",
                    known_address="0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B",
                    linkedin_username="vitalik-buterin",
                    medium_username="vitalikbuterin",
                    so_username="vitalikbuterin",
                    personal_website="vitalik.ca"
                ) for source in template["sources"]
            ]
            for source in template_sources:
                if source not in sources:
                    sources.append(source)
        
        if "search_queries" in template:
            template_queries = [
                query.format(
                    entity=entity,
                    year="2015",
                    current_project="Ethereum"
                ) for query in template["search_queries"]
            ]
            for query in template_queries:
                if query not in search_queries:
                    search_queries.append(query)
        
        # Prepare the result
        strategy = {
            "objective": objective,
            "entity": entity,
            "artifact_type": artifact_type,
            "llm_response": llm_response,
            "sources": sources,
            "search_queries": search_queries,
            "github_repos": github_repos,
            "usernames": usernames,
            "crawlable_urls": [],  # Will be populated below
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate crawlable URLs
        crawlable_urls = []
        
        # Normalize and add direct sources
        normalized_sources = []
        for source in sources:
            if not source.startswith(('http://', 'https://')):
                normalized_sources.append(f"https://{source}")
            else:
                normalized_sources.append(source)
        crawlable_urls.extend(normalized_sources)
        
        # Normalize and add GitHub repositories
        normalized_repos = []
        for repo in github_repos:
            if not repo.startswith(('http://', 'https://')):
                normalized_repos.append(f"https://{repo}")
            else:
                normalized_repos.append(repo)
        crawlable_urls.extend(normalized_repos)
        
        # Add search engine queries
        for query in search_queries:
            encoded_query = quote_plus(query)
            crawlable_urls.append(f"https://duckduckgo.com/html/?q={encoded_query}")
            crawlable_urls.append(f"https://github.com/search?q={encoded_query}&type=code")
        
        # Add Twitter searches
        for username in usernames:
            crawlable_urls.append(f"https://twitter.com/{username}")
        
        # Add wayback machine URLs for important sources
        important_domains = ["vitalik.ca", "ethereum.org", "github.com/vbuterin", "github.com/ethereum"]
        for domain in important_domains:
            if not domain.startswith(('http://', 'https://')):
                domain = f"https://{domain}"
            crawlable_urls.append(f"https://web.archive.org/web/*/https://{domain.replace('https://', '')}")
        
        # Deduplicate URLs
        strategy["crawlable_urls"] = list(set(crawlable_urls))
        
        # Cache the strategy
        self.strategy_cache[cache_key] = strategy
        
        return strategy

if __name__ == "__main__":
    # Test the strategy generator
    strategy_generator = LLMResearchStrategy()
    
    test_objective = "Find name artifacts around Vitalik Buterin"
    test_entity = "Vitalik Buterin"
    
    strategy = strategy_generator.generate_research_strategy(test_objective, test_entity)
    
    print(f"Generated Research Strategy for: {test_objective}")
    print(f"Found {len(strategy['crawlable_urls'])} crawlable URLs")
    print(f"Search Queries: {len(strategy['search_queries'])}")
    print("\nSample URLs:")
    for url in strategy['crawlable_urls'][:5]:
        print(f"- {url}")
    
    print("\nSample Search Queries:")
    for query in strategy['search_queries'][:5]:
        print(f"- {query}")