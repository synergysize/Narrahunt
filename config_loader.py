#!/usr/bin/env python3
"""
Configuration Loader for Narrahunt Phase 2.

This module handles loading of configuration from environment variables
and provides centralized access to API keys and other configuration settings.
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Configure logging
base_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(base_dir, 'logs'), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(base_dir, 'logs', 'config.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('config_loader')

# Load environment variables from .env file
load_dotenv()

# Required API keys for the application
REQUIRED_API_KEYS = [
    'CLAUDE_API_KEY',
    'OPENAI_API_KEY'
]

# Optional API keys
OPTIONAL_API_KEYS = [
    'GITHUB_API_KEY',
    'GOOGLE_API_KEY',
    'ETHERSCAN_API_KEY'
]

def get_api_key(key_name: str, required: bool = False) -> Optional[str]:
    """
    Get an API key from environment variables.
    
    Args:
        key_name: Name of the API key environment variable
        required: Whether the API key is required for application function
        
    Returns:
        The API key if found, None otherwise
        
    Raises:
        ValueError: If the API key is required but not found
    """
    api_key = os.getenv(key_name)
    
    if not api_key and required:
        error_msg = f"Required API key '{key_name}' not found in environment variables. Please add it to your .env file."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    if not api_key:
        logger.warning(f"API key '{key_name}' not found in environment variables.")
        return None
    
    # Mask the API key for logging (show only first 4 and last 4 characters)
    if len(api_key) > 8:
        masked_key = f"{api_key[:4]}...{api_key[-4:]}"
    else:
        masked_key = "****"
    
    logger.info(f"Loaded API key '{key_name}': {masked_key}")
    return api_key

def validate_required_keys() -> bool:
    """
    Validate that all required API keys are present.
    
    Returns:
        True if all required keys are present, False otherwise
    """
    missing_keys = []
    
    for key_name in REQUIRED_API_KEYS:
        if not os.getenv(key_name):
            missing_keys.append(key_name)
    
    if missing_keys:
        logger.error(f"Missing required API keys: {', '.join(missing_keys)}")
        logger.error("Please add these keys to your .env file.")
        return False
    
    logger.info("All required API keys are present.")
    return True

def get_all_config() -> Dict[str, Any]:
    """
    Get all configuration settings as a dictionary.
    
    Returns:
        Dictionary of all configuration settings
    """
    config = {}
    
    # Add all API keys
    for key_name in REQUIRED_API_KEYS + OPTIONAL_API_KEYS:
        config[key_name] = os.getenv(key_name)
    
    # Add other configuration settings
    config['LOG_LEVEL'] = os.getenv('LOG_LEVEL', 'INFO')
    config['CACHE_DIR'] = os.getenv('CACHE_DIR', os.path.join(base_dir, 'cache'))
    config['RESULTS_DIR'] = os.getenv('RESULTS_DIR', os.path.join(base_dir, 'results'))
    
    return config

def init_config() -> Dict[str, Any]:
    """
    Initialize the configuration system and validate required keys.
    
    Returns:
        Dictionary of configuration settings
    
    Raises:
        ValueError: If required API keys are missing and STRICT_CONFIG=True
    """
    # Load environment variables
    load_dotenv()
    
    # Create .env file if it doesn't exist
    env_path = os.path.join(base_dir, '.env')
    if not os.path.exists(env_path):
        logger.warning(".env file not found, creating a template...")
        with open(env_path, 'w') as f:
            f.write("# Narrahunt Phase 2 Configuration\n\n")
            f.write("# Required API keys\n")
            for key in REQUIRED_API_KEYS:
                f.write(f"{key}=\n")
            f.write("\n# Optional API keys\n")
            for key in OPTIONAL_API_KEYS:
                f.write(f"# {key}=\n")
            f.write("\n# Configuration settings\n")
            f.write("LOG_LEVEL=INFO\n")
            f.write("STRICT_CONFIG=False\n")
        logger.info(f"Created template .env file at {env_path}")
    
    # Validate required keys
    if not validate_required_keys() and os.getenv('STRICT_CONFIG', 'False').lower() == 'true':
        raise ValueError("Missing required API keys and STRICT_CONFIG is enabled")
    
    # Return all configuration
    return get_all_config()

# Initialize configuration on module import
config = init_config()

if __name__ == "__main__":
    print("Testing configuration loader...")
    print(f"Required API keys: {REQUIRED_API_KEYS}")
    print(f"Optional API keys: {OPTIONAL_API_KEYS}")
    print("Validating required keys...")
    valid = validate_required_keys()
    print(f"All required keys present: {valid}")
    
    # Test getting a specific key
    for key in REQUIRED_API_KEYS:
        try:
            value = get_api_key(key, required=True)
            print(f"  {key}: {'Present' if value else 'Missing'}")
        except ValueError as e:
            print(f"  {key}: Error - {str(e)}")
    
    print("\nConfiguration complete.")