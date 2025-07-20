#!/usr/bin/env python3
"""
Verify API Keys for Narrahunt Phase 2.

This script tests whether the API keys loaded from the .env file
are valid by making simple API calls to the respective services.
"""

import os
import json
import requests
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('verify_api_keys')

def verify_claude_api_key(api_key):
    """Verify Claude API key by making a simple API call."""
    if not api_key:
        return False, "API key not found"

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    data = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "Say hello"}]
    }
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return True, "Valid"
        else:
            return False, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Exception: {str(e)}"

def verify_openai_api_key(api_key):
    """Verify OpenAI API key by making a simple API call."""
    if not api_key:
        return False, "API key not found"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return True, "Valid"
        else:
            return False, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Exception: {str(e)}"

def main():
    """Main function to verify all API keys."""
    # Print current working directory
    current_dir = os.getcwd()
    logger.info(f"Current working directory: {current_dir}")
    
    # Check if .env file exists
    env_path = os.path.join(current_dir, '.env')
    env_exists = os.path.exists(env_path)
    logger.info(f".env file exists at {env_path}: {env_exists}")
    
    # Load environment variables from .env file
    load_result = load_dotenv(env_path)
    logger.info(f"load_dotenv() returned: {load_result}")
    
    # Get API keys
    claude_api_key = os.getenv('CLAUDE_API_KEY')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    # Verify Claude API key
    logger.info("Verifying Claude API key...")
    claude_valid, claude_message = verify_claude_api_key(claude_api_key)
    logger.info(f"Claude API key: {'Valid' if claude_valid else 'Invalid'} - {claude_message}")
    
    # Verify OpenAI API key
    logger.info("Verifying OpenAI API key...")
    openai_valid, openai_message = verify_openai_api_key(openai_api_key)
    logger.info(f"OpenAI API key: {'Valid' if openai_valid else 'Invalid'} - {openai_message}")
    
    # Print summary
    print("\n=== API Key Verification Summary ===")
    print(f"Claude API key: {'Present' if claude_api_key else 'Missing'} - {'Valid' if claude_valid else 'Invalid'}")
    print(f"OpenAI API key: {'Present' if openai_api_key else 'Missing'} - {'Valid' if openai_valid else 'Invalid'}")

if __name__ == "__main__":
    main()