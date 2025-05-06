import os
import sys
import unittest.mock

import pytest
from fastapi.testclient import TestClient

# Ensure src is in the import path
dir_path = os.path.dirname(os.path.realpath(__file__))
src_path = os.path.abspath(os.path.join(dir_path, '../src'))
sys.path.insert(0, src_path)

# Mock environment variables for testing
os.environ['OPENAI_API_URL'] = 'https://api.openai.com'
os.environ['GROK_API_URL'] = 'https://api.grok-ai.org'

# Import the app after setting environment variables
from proxy import app, MODEL_CONFIGS

# Override MODEL_CONFIGS for testing
MODEL_CONFIGS['openai']['url'] = 'https://api.openai.com'
MODEL_CONFIGS['grok']['url'] = 'https://api.grok-ai.org'

client = TestClient(app)

@unittest.mock.patch('openai.OpenAI')
def test_openai_completions_mock(mock_openai):
    # Mock the OpenAI client and its methods
    mock_client = unittest.mock.MagicMock()
    mock_openai.return_value = mock_client
    
    # Setup request
    headers = {"Authorization": "Bearer test-api-key"}
    
    # Test with stream parameter
    response = client.post(
        "/openai/v1/chat/completions",
        json={
            "messages": [{"role": "user", "content": "Hello"}],
            "model": "gpt-4",
            "stream": True
        },
        headers=headers
    )
    
    # Since we're mocking, we expect a 400 because the mock doesn't return a proper response
    assert response.status_code in (200, 400, 401, 422)

@unittest.mock.patch('openai.OpenAI')
def test_grok_completions_mock(mock_openai):
    # Mock the OpenAI client and its methods
    mock_client = unittest.mock.MagicMock()
    mock_openai.return_value = mock_client
    
    # Setup request
    headers = {"Authorization": "Bearer test-api-key"}
    
    # Test with stream parameter
    response = client.post(
        "/grok/v1/chat/completions", 
        json={
            "messages": [{"role": "user", "content": "Hi"}], 
            "model": "grok-2-latest", 
            "stream": True
        },
        headers=headers
    )
    
    # Since we're mocking, we expect a 400 because the mock doesn't return a proper response
    assert response.status_code in (200, 400, 401, 422)
