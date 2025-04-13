"""
Pytest configuration file for the backend tests.
"""
import pytest
import os
import sys
import json
from unittest.mock import patch

# Add the parent directory to the path so we can import the main module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def mock_config():
    """Fixture to provide a mock configuration for testing."""
    return {
        "api_keys": {
            "openai": "mock-openai-key",
            "grok": "mock-grok-key",
            "qwen": "mock-qwen-key",
            "deepseek": "mock-deepseek-key"
        },
        "api_urls": {
            "openai": "https://api.openai.com/v1/chat/completions",
            "grok": "https://api.groq.com/openai/v1/chat/completions",
            "qwen": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            "deepseek": "https://api.deepseek.com/v1/chat/completions"
        },
        "models": {
            "openai": "gpt-3.5-turbo",
            "grok": "grok-2-latest",
            "qwen": "qwen-plus",
            "deepseek": "deepseek-chat"
        },
        "server": {
            "host": "localhost",
            "port": 8000,
            "debug": True
        }
    }

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture to set up mock environment variables for testing."""
    # Set up environment variables
    monkeypatch.setenv("OPENAI_API_KEY", "env-openai-key")
    monkeypatch.setenv("GROK_API_KEY", "env-grok-key")
    monkeypatch.setenv("QWEN_API_KEY", "env-qwen-key")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "env-deepseek-key")
    
    # Return the values for reference
    return {
        "OPENAI_API_KEY": "env-openai-key",
        "GROK_API_KEY": "env-grok-key",
        "QWEN_API_KEY": "env-qwen-key",
        "DEEPSEEK_API_KEY": "env-deepseek-key"
    }

@pytest.fixture
def test_messages():
    """Fixture to provide test messages for API calls."""
    return [{"role": "user", "content": "Hello, how are you?"}]
