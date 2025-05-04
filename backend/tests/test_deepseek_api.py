"""
Test cases for the DeepSeek API integration.
"""
import pytest
import asyncio
import os
import sys
from unittest.mock import patch, MagicMock, AsyncMock
import json

# Add the parent directory to the path so we can import the main module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.utils.model_helpers import call_deepseek
from backend.env_config import get_api_key

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
    with patch('backend.utils.model_helpers.get_client') as mock_get_client:
        # Configure the mock client
        mock_client = MagicMock()
        mock_completions = MagicMock()
        mock_chat = MagicMock()
        mock_client.chat = mock_chat
        mock_chat.completions = mock_completions
        
        # Configure the response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = MOCK_RESPONSE["choices"][0]["message"]["content"]
        
        # Use AsyncMock for the async method
        mock_completions.create = AsyncMock(return_value=mock_response)
        
        # Return our mock client when get_client is called
        mock_get_client.return_value = mock_client

        # Call the function with a user-provided key
        result = await call_deepseek(TEST_MESSAGES, TEST_API_KEY, stream=False)

        # Check that the client was created with the correct key
        mock_get_client.assert_called_once_with("deepseek", TEST_API_KEY)
        
        # Check that completions.create was called with the correct parameters
        mock_completions.create.assert_called_once()
        args, kwargs = mock_completions.create.call_args
        assert 'messages' in kwargs
        assert kwargs['messages'] == TEST_MESSAGES
        assert 'stream' in kwargs
        assert kwargs['stream'] is False
        
        # Check the result
        assert result == {"content": MOCK_RESPONSE["choices"][0]["message"]["content"], "model": "deepseek"}

@pytest.mark.asyncio
async def test_call_deepseek_with_environment_key():
    """Test that call_deepseek falls back to the environment key."""
    with patch('backend.utils.model_helpers.get_client') as mock_get_client, \
         patch('backend.utils.model_helpers.get_api_key', return_value='env-deepseek-api-key'):
        # Configure the mock client
        mock_client = MagicMock()
        mock_completions = MagicMock()
        mock_chat = MagicMock()
        mock_client.chat = mock_chat
        mock_chat.completions = mock_completions
        
        # Configure the response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = MOCK_RESPONSE["choices"][0]["message"]["content"]
        
        # Use AsyncMock for the async method
        mock_completions.create = AsyncMock(return_value=mock_response)
        
        # Return our mock client when get_client is called
        mock_get_client.return_value = mock_client

        # Call the function without a user-provided key
        result = await call_deepseek(TEST_MESSAGES, stream=False)

        # Check that the client was created with None as the key (will use environment)
        mock_get_client.assert_called_once_with("deepseek", None)
        
        # Check the result
        assert result == {"content": MOCK_RESPONSE["choices"][0]["message"]["content"], "model": "deepseek"}

@pytest.mark.asyncio
async def test_call_deepseek_error_response():
    """Test that call_deepseek handles error responses correctly."""
    with patch('backend.utils.model_helpers.get_client') as mock_get_client:
        # Configure the mock client
        mock_client = MagicMock()
        mock_completions = MagicMock()
        mock_chat = MagicMock()
        mock_client.chat = mock_chat
        mock_chat.completions = mock_completions
        
        # Configure the completions.create to raise an exception
        # Use AsyncMock for the async method
        mock_completions.create = AsyncMock(side_effect=Exception("401 Unauthorized"))
        
        # Return our mock client when get_client is called
        mock_get_client.return_value = mock_client

        # Call the function and check that it raises an exception
        with pytest.raises(Exception) as excinfo:
            await call_deepseek(TEST_MESSAGES, TEST_API_KEY, stream=False)
        
        assert "401" in str(excinfo.value)

@pytest.mark.asyncio
async def test_call_deepseek_no_key():
    """Test that call_deepseek raises an exception when no key is available."""
    with patch('backend.utils.model_helpers.get_api_key', return_value=None):
        # Call the function without a key and check that it raises an exception
        with pytest.raises(Exception) as excinfo:
            await call_deepseek(TEST_MESSAGES, stream=False)
        
        assert "API key not configured" in str(excinfo.value)

# Run the tests if this file is executed directly
@pytest.mark.asyncio
async def test_call_deepseek_streaming_mode():
    """Test that call_deepseek works in streaming mode."""
    with patch('backend.utils.model_helpers.call_deepseek_stream') as mock_stream_func:
        # Mock the streaming response generator
        async def mock_stream_generator():
            yield "Hello"
            yield " world"
        
        # Set up the mock for call_deepseek_stream
        mock_stream_func.return_value = mock_stream_generator()
        
        # Call the function with streaming
        response = await call_deepseek(TEST_MESSAGES, TEST_API_KEY, stream=True)
        
        # Verify the response is a StreamingResponse
        from fastapi.responses import StreamingResponse
        assert isinstance(response, StreamingResponse)
        
        # Verify that call_deepseek_stream was called with the correct parameters
        mock_stream_func.assert_called_once_with(TEST_MESSAGES, TEST_API_KEY, "en")

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
