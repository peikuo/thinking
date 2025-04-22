"""
Environment-based configuration module for the Thinking API.
This module loads API keys and other configuration from environment variables.
"""
import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log level constants
LOG_LEVEL_DEBUG = "debug"
LOG_LEVEL_INFO = "info"
LOG_LEVEL_WARNING = "warning"
LOG_LEVEL_ERROR = "error"
LOG_LEVEL_CRITICAL = "critical"

# Environment constants
ENV_DEV = "dev"
ENV_TEST = "test"
ENV_PRD = "prd"

# Default configuration values
DEFAULT_CONFIG = {
    "api_keys": {
        "openai": "",
        "grok": "",
        "qwen": "",
        "deepseek": "",
        "glm": "",
        "doubao": ""
    },
    "api_urls": {
        "openai": "https://api.openai.com/v1/chat/completions",
        "grok": "https://api.x.ai/v1",
        "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "deepseek": "https://api.deepseek.com",
        "glm": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "doubao": "https://ark.cn-beijing.volces.com/api/v3"
    },
    "models": {
        "openai": "gpt-4o-mini",
        "grok": "grok-2-latest",
        "qwen": "qwen-plus",
        "deepseek": "deepseek-chat",
        "doubao": "doubao-1-5-pro-32k-250115"
    },
    "server": {
        "host": "localhost",
        "port": 8000,
        "debug": True,
        "log_level": "debug"
    }
}

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

def get_api_key(provider: str) -> str:
    """
    Get API key for a specific provider from environment variables.
    
    Args:
        provider: The provider name (openai, grok, qwen, deepseek)
        
    Returns:
        The API key for the provider
    """
    env_var_name = f"{provider.upper()}_API_KEY"
    api_key = os.environ.get(env_var_name, "")
    
    if not api_key:
        logger.warning(f"No API key found for {provider}. Set {env_var_name} environment variable.")
    
    return api_key

def get_api_url(provider: str) -> str:
    """
    Get API URL for a specific provider from environment variables.
    
    Args:
        provider: The provider name (openai, grok, qwen, deepseek)
        
    Returns:
        The API URL for the provider
    """
    env_var_name = f"{provider.upper()}_API_URL"
    api_url = os.environ.get(env_var_name, DEFAULT_CONFIG["api_urls"].get(provider, ""))
    
    return api_url

def get_model(provider: str) -> str:
    """
    Get model name for a specific provider from environment variables.
    
    Args:
        provider: The provider name (openai, grok, qwen, deepseek)
        
    Returns:
        The model name for the provider
    """
    env_var_name = f"{provider.upper()}_MODEL"
    model = os.environ.get(env_var_name, DEFAULT_CONFIG["models"].get(provider, ""))
    
    return model

def get_server_config(key: str, default: Any = None) -> Any:
    """
    Get server configuration value from environment variables.
    
    Args:
        key: The configuration key
        default: Default value if not found
        
    Returns:
        The configuration value
    """
    if key == "host":
        return os.environ.get("SERVER_HOST", DEFAULT_CONFIG["server"]["host"])
    elif key == "port":
        port_str = os.environ.get("SERVER_PORT", str(DEFAULT_CONFIG["server"]["port"]))
        try:
            return int(port_str)
        except ValueError:
            logger.warning(f"Invalid port: {port_str}, using default: {DEFAULT_CONFIG['server']['port']}")
            return DEFAULT_CONFIG["server"]["port"]
    elif key == "debug":
        debug_str = os.environ.get("SERVER_DEBUG", str(DEFAULT_CONFIG["server"]["debug"]))
        return debug_str.lower() in ("true", "1", "yes")
    elif key == "log_level":
        return os.environ.get("LOG_LEVEL", DEFAULT_CONFIG["server"]["log_level"]).lower()
    else:
        return default

def switch_environment(env: str) -> None:
    """
    Switch the current environment.
    This function is kept for compatibility but doesn't do anything meaningful
    in the environment variable-based configuration.
    
    Args:
        env: The environment to switch to
    """
    if env not in [ENV_DEV, ENV_TEST, ENV_PRD]:
        logger.warning(f"Unknown environment: {env}, ignoring")
        return
    
    logger.info(f"Switched to environment: {env}")
    os.environ["THINKING_ENV"] = env

def get_current_env() -> str:
    """
    Get the current environment.
    
    Returns:
        The current environment
    """
    return get_environment()


def get_log_level() -> str:
    """
    Get the log level from environment variables.
    
    Returns:
        The log level (debug, info, warning, error, critical)
    """
    log_level = os.environ.get("LOG_LEVEL", LOG_LEVEL_INFO).lower()
    valid_levels = [LOG_LEVEL_DEBUG, LOG_LEVEL_INFO, LOG_LEVEL_WARNING, LOG_LEVEL_ERROR, LOG_LEVEL_CRITICAL]
    
    if log_level not in valid_levels:
        logger.warning(f"Invalid log level: {log_level}, defaulting to {LOG_LEVEL_INFO}")
        return LOG_LEVEL_INFO
    
    return log_level
