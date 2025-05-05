"""
Test cases for the DeepSeek API integration.
"""
import asyncio
import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient, Response

# Add the parent directory to the path so we can import the main module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.env_config import get_api_key
from backend.utils.model_helpers import call_deepseek

# Test data
TEST_MESSAGES = [{"role": "user", "content": "Hello, how are you?"}]
TEST_API_KEY = "test-deepseek-api-key"
MOCK_RESPONSE = {
    "choices": [
        {
            "message": {
                "content": "I'm DeepSeek, an AI assistant. I don't have feelings, but I'm functioning properly and ready to assist you. How can I help you today?"
            }
        }
    ]
}

@pytest.mark.asyncio
async def test_call_deepseek_with_user_key():
    """Test that call_deepseek uses the provided API key."""
    with patch('httpx.AsyncClient.post') as mock_post:
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_RESPONSE
        mock_post.return_value = mock_response

        # Call the function with a user-provided key
        result = await call_deepseek(TEST_MESSAGES, TEST_API_KEY, use_streaming=False)

        # Check that the API was called with the correct key
        mock_post.assert_called_once()
        kwargs = mock_post.call_args.kwargs
        assert kwargs['headers']['Authorization'] == f"Bearer {TEST_API_KEY}"
        
        # Check the request format
        request_body = json.loads(kwargs['content'])
        assert 'messages' in request_body
        assert 'stream' in request_body
        assert request_body['stream'] is False
        assert 'model' in request_body
        
        # Check the result
        assert result == MOCK_RESPONSE["choices"][0]["message"]["content"]

@pytest.mark.asyncio
async def test_call_deepseek_with_environment_key():
    """Test that call_deepseek falls back to the environment key."""
    with patch('httpx.AsyncClient.post') as mock_post, \
         patch('main.DEEPSEEK_API_KEY', 'env-deepseek-api-key'):
        # Configure the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_RESPONSE
        mock_post.return_value = mock_response

        # Call the function without a user-provided key
        result = await call_deepseek(TEST_MESSAGES, use_streaming=False)

        # Check that the API was called with the environment key
        mock_post.assert_called_once()
        kwargs = mock_post.call_args.kwargs
        assert kwargs['headers']['Authorization'] == "Bearer env-deepseek-api-key"
        
        # Check the result
        assert result == MOCK_RESPONSE["choices"][0]["message"]["content"]

@pytest.mark.asyncio
async def test_call_deepseek_error_response():
    """Test that call_deepseek handles error responses correctly."""
    with patch('httpx.AsyncClient.post') as mock_post:
        # Configure the mock to return an error
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        # Call the function and check that it raises an exception
        with pytest.raises(Exception) as excinfo:
            await call_deepseek(TEST_MESSAGES, TEST_API_KEY, use_streaming=False)
        
        assert "401" in str(excinfo.value)

@pytest.mark.asyncio
async def test_call_deepseek_no_key():
    """Test that call_deepseek raises an exception when no key is available."""
    with patch('main.DEEPSEEK_API_KEY', None):
        # Call the function without a key and check that it raises an exception
        with pytest.raises(Exception) as excinfo:
            await call_deepseek(TEST_MESSAGES, use_streaming=False)
        
        assert "API key not configured" in str(excinfo.value)

# Run the tests if this file is executed directly
@pytest.mark.asyncio
async def test_call_deepseek_streaming_mode():
    """Test that call_deepseek works in streaming mode."""
    with patch('main.AsyncOpenAI') as mock_client_class:
        # Configure the mock client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Configure the mock streaming response
        mock_stream = MagicMock()
        mock_client.chat.completions.create.return_value = mock_stream
        
        # Mock the streaming chunks
        chunk1 = MagicMock()
        chunk1.choices = [MagicMock()]
        chunk1.choices[0].delta.content = "Hello"
        
        chunk2 = MagicMock()
        chunk2.choices = [MagicMock()]
        chunk2.choices[0].delta.content = " world"
        
        # Configure the async iterator behavior
        mock_stream.__aiter__.return_value = [chunk1, chunk2].__aiter__()
        
        # Call the function in streaming mode
        from fastapi.responses import StreamingResponse
        result = await call_deepseek(TEST_MESSAGES, TEST_API_KEY, use_streaming=True)
        
        # Check that the result is a StreamingResponse
        assert isinstance(result, StreamingResponse)
        
        # Check that the API was called with use_streaming=True
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs['stream'] is True

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
