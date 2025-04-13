"""
Configuration module for the Thinking API.
This module loads API keys and other configuration from environment-specific JSON files.
"""
import json
import os
import logging
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment constants
ENV_DEV = "dev"
ENV_TEST = "test"
ENV_PRD = "prd"

# Config directory
CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")

# Default configuration values
DEFAULT_CONFIG = {
    "api_keys": {
        "openai": "",
        "grok": "",
        "qwen": "",
        "deepseek": ""
    },
    "api_urls": {
        "openai": "https://api.openai.com/v1/chat/completions",
        "grok": "https://api.groq.com/openai/v1/chat/completions",
        "qwen": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
        "deepseek": "https://api.deepseek.com/v1/chat/completions"
    },
    "models": {
        "openai": "gpt-4o",
        "grok": "llama3-70b-8192",
        "qwen": "qwen-max",
        "deepseek": "deepseek-chat"
    },
    "server": {
        "host": "0.0.0.0",
        "port": 8000,
        "debug": False,
        "log_level": "info"
    }
}

# Global configuration
config: Dict[str, Any] = {}
current_env: str = ENV_DEV  # Default environment

def get_environment() -> str:
    """
    Get the current environment from the THINKING_ENV environment variable.
    Defaults to development if not set.
    
    Returns:
        Current environment (dev, test, or prod)
    """
    env = os.environ.get("THINKING_ENV", ENV_DEV).lower()
    
    if env not in [ENV_DEV, ENV_TEST, ENV_PRD]:
        logger.warning(f"Unknown environment: {env}, defaulting to {ENV_DEV}")
        return ENV_DEV
        
    return env

def get_config_path(env: Optional[str] = None) -> str:
    """
    Get the configuration file path for the specified environment.
    
    Args:
        env: Environment name (dev, test, or prod)
        
    Returns:
        Path to the configuration file
    """
    if env is None:
        env = get_environment()
        
    return os.path.join(CONFIG_DIR, f"config_{env}.json")

def load_config(env: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a JSON file for the specified environment.
    If the file doesn't exist, create it with default values.
    
    Args:
        env: Environment name (dev, test, or prod)
        
    Returns:
        Dict containing the configuration
    """
    global config, current_env
    
    if env is None:
        env = get_environment()
    
    current_env = env
    config_path = get_config_path(env)
    
    # Create config directory if it doesn't exist
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    # Create default config if it doesn't exist
    if not os.path.exists(config_path):
        with open(config_path, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        logger.info(f"Created default configuration at {config_path}")
        config = DEFAULT_CONFIG
        return config
    
    # Load existing config
    try:
        with open(config_path, 'r') as f:
            loaded_config = json.load(f)
        
        # Ensure all required keys are present
        for section, values in DEFAULT_CONFIG.items():
            if section not in loaded_config:
                loaded_config[section] = values
            else:
                for key, value in values.items():
                    if key not in loaded_config[section]:
                        loaded_config[section][key] = value
        
        config = loaded_config
        logger.info(f"Loaded configuration for environment: {env}")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        logger.warning("Using default configuration")
        config = DEFAULT_CONFIG
        return config

def get_api_key(provider: str) -> str:
    """Get API key for a specific provider"""
    return config.get("api_keys", {}).get(provider, "")

def get_api_url(provider: str) -> str:
    """Get API URL for a specific provider"""
    return config.get("api_urls", {}).get(provider, "")

def get_model(provider: str) -> str:
    """Get model name for a specific provider"""
    return config.get("models", {}).get(provider, "")

def get_server_config(key: str, default: Any = None) -> Any:
    """Get server configuration value"""
    return config.get("server", {}).get(key, default)

def get_current_env() -> str:
    """Get the current environment"""
    return current_env

def switch_environment(env: str) -> Dict[str, Any]:
    """Switch to a different environment and reload configuration"""
    if env not in [ENV_DEV, ENV_TEST, ENV_PRD]:
        raise ValueError(f"Invalid environment: {env}. Must be one of: {ENV_DEV}, {ENV_TEST}, {ENV_PRD}")
    
    return load_config(env)

# Load configuration on module import
load_config()
