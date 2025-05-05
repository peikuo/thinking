"""
Helpers for model integration and API proxying in the Thinking backend.
"""
import asyncio
import json
import os
import sys
import time
import traceback
from functools import wraps
from typing import Dict, List, Literal, Optional

import httpx
from fastapi import HTTPException, Request
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI

# Add the parent directory to path to support both running methods
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from ..env_config import get_api_key, get_api_url, get_model
    from .logger import logger
    from .summary_prompts import get_summary_prompt
except (ImportError, ValueError):
    from backend.env_config import get_api_key, get_api_url, get_model
    from backend.utils.logger import logger
    from backend.utils.summary_prompts import get_summary_prompt

# Constants
DEFAULT_TIMEOUT = 60.0  # Default timeout for API calls (in seconds)
MAX_RETRIES_COUNT = 6   # Maximum number of retries for API calls

# Provider types
ProviderType = Literal["openai", "glm", "doubao", "grok", "qwen", "deepseek"]

# Shared clients for APIs (initialized on demand)
_clients: Dict[str, AsyncOpenAI] = {}
_httpx_client: Optional[httpx.AsyncClient] = None  # Legacy httpx client

def get_client(provider_name: ProviderType, api_key: str = None) -> AsyncOpenAI:
    """
    Get or create a shared client for the specified provider.
    
    This factory function creates and caches API clients for different LLM providers.
    All clients use the OpenAI-compatible interface.
    
    Args:
        provider: The provider name (openai, glm, doubao, grok, qwen, deepseek)
        api_key: Optional API key to use, defaults to environment variable
        
    Returns:
        AsyncOpenAI client instance configured for the specified provider
        
    Raises:
        HTTPException: If the API key is not configured
    """
    global _clients
    
    # Use user-provided key if available, otherwise use environment variable
    key_to_use = api_key or get_api_key(provider_name)
    api_url = get_api_url(provider_name)
    
    if not key_to_use:
        raise HTTPException(status_code=500, detail=f"{provider_name.upper()} API key not configured")
        
    # Create a client if we don't have one for this provider/key combination
    client_key = f"{provider_name}:{key_to_use}"
    if client_key not in _clients or _clients[provider_name].api_key != key_to_use:
        _clients[provider_name] = AsyncOpenAI(
            api_key=key_to_use,
            max_retries=MAX_RETRIES_COUNT,
            base_url=api_url,
            timeout=DEFAULT_TIMEOUT
        )
    
    return _clients[provider_name]

# Provider-specific client getters (for backward compatibility)
def get_openai_client(api_key: str = None) -> AsyncOpenAI:
    """Get or create a shared OpenAI client"""
    return get_client("openai", api_key)

def get_glm_client(api_key: str = None) -> AsyncOpenAI:
    """Get or create a shared GLM client"""
    return get_client("glm", api_key)

def get_doubao_client(api_key: str = None) -> AsyncOpenAI:
    """Get or create a shared Doubao client"""
    return get_client("doubao", api_key)

def get_grok_client(api_key: str = None) -> AsyncOpenAI:
    """Get or create a shared Grok client"""
    return get_client("grok", api_key)

def get_qwen_client(api_key: str = None) -> AsyncOpenAI:
    """Get or create a shared Qwen client"""
    return get_client("qwen", api_key)

def get_deepseek_client(api_key: str = None) -> AsyncOpenAI:
    """Get or create a shared DeepSeek client"""
    return get_client("deepseek", api_key)

def api_error_handler(provider_name: str):
    """
    Decorator for handling API call errors consistently.
    
    Args:
        provider_name: The provider name for error messages
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except httpx.HTTPStatusError as e:
                error_msg = f"HTTP error from {provider_name.upper()} API: {e.response.status_code} - {e.response.text}"
                logger.error(error_msg)
                logger.debug(traceback.format_exc())
                raise HTTPException(status_code=e.response.status_code, detail=f"{provider_name.upper()} API HTTP error: {e.response.text}")
            except httpx.RequestError as e:
                error_msg = f"Request error to {provider_name.upper()} API: {str(e)}"
                logger.error(error_msg)
                logger.debug(traceback.format_exc())
                raise HTTPException(status_code=503, detail=f"{provider_name.upper()} API connection error: {str(e)}")
            except json.JSONDecodeError as e:
                error_msg = f"JSON decode error from {provider_name.upper()} API: {str(e)}"
                logger.error(error_msg)
                logger.debug(traceback.format_exc())
                raise HTTPException(status_code=500, detail=f"{provider_name.upper()} API returned invalid JSON: {str(e)}")
            except Exception as e:
                error_msg = f"Failed to call {provider_name.upper()} API: {str(e)}"
                logger.error(error_msg)
                logger.debug(traceback.format_exc())
                raise HTTPException(status_code=500, detail=f"{provider_name.upper()} API error: {str(e)}")

        return wrapper
    return decorator

def get_httpx_client() -> httpx.AsyncClient:
    """
    Get or create a shared httpx client for HTTP-based APIs.
    
    Returns:
        httpx.AsyncClient instance
    """
    global _httpx_client
    
    if _httpx_client is None:
        _httpx_client = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)
    
    return _httpx_client

# Helper function to decode API key from header
def decode_api_key(req: Request, header_name: str) -> Optional[str]:
    from urllib.parse import unquote
    api_key = req.headers.get(header_name)
    if api_key:
        return unquote(api_key)
    return None

# Helper functions for API calls
# Generic streaming function template
async def stream_llm_response(provider: ProviderType, messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """
    Generic streaming function for LLM API calls.
    
    Args:
        provider: The provider name (openai, glm, etc.)
        messages: List of message objects with role and content
        api_key: Optional API key to use
        language: Language code (en or zh)
        
    Yields:
        Text chunks from the streaming response
    """
    client = get_client(provider, api_key)
    model_name = get_model(provider)
    
    try:
        response_stream = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True
        )
        
        # For a streaming response, yield only the delta content
        async for chunk in response_stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    except Exception as e:
        logger.error(f"Error in {provider} streaming response: {str(e)}")
        # Yield an error message that can be handled by the client
        yield f"\n\nError: {str(e)}"
        # Re-raise the exception to be handled by the error handler decorator
        raise

# Generic non-streaming function template
async def get_llm_response(provider: ProviderType, messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """
    Generic non-streaming function for LLM API calls.
    
    Args:
        provider: The provider name (openai, glm, etc.)
        messages: List of message objects with role and content
        api_key: Optional API key to use
        language: Language code (en or zh)
        
    Returns:
        Dictionary with the response content
    """
    client = get_client(provider, api_key)
    model_name = get_model(provider)
    
    response = await client.chat.completions.create(
        model=model_name,
        messages=messages,
        stream=False
    )
    
    return {"content": response.choices[0].message.content, "model": provider}

# OpenAI API functions
@api_error_handler("openai")
async def stream_openai_response(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Streaming version of the OpenAI API call"""
    async for chunk in stream_llm_response("openai", messages, api_key, language):
        yield chunk

@api_error_handler("openai")
async def get_openai_response(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Non-streaming version of the OpenAI API call"""
    return await get_llm_response("openai", messages, api_key, language)

@api_error_handler("openai")
async def call_openai(messages: List[Dict[str, str]], api_key: str = None, use_streaming: bool = False, language: str = "en"):
    """Direct implementation of OpenAI API call with streaming support"""
    if use_streaming:
        # For streaming, implement the streaming logic directly here
        # Get the API key and model name
        key_to_use = api_key or get_api_key("openai")
        model_name = get_model("openai")
        
        # Define the streaming response generator
        async def stream_response_generator():
            try:
                # Get the client
                client = get_openai_client(key_to_use)
                
                # Make the API call directly
                response = await client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    stream=True
                )
                
                # Process the streaming response
                async for chunk in response:
                    if hasattr(chunk, 'choices') and chunk.choices and hasattr(chunk.choices[0], 'delta'):
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            content = delta.content
                            yield f"data: {json.dumps({'content': content, 'model': 'openai'})}\n\n"
                
                # Send a final empty data message to properly close the stream
                yield f"data: {json.dumps({'content': '', 'model': 'openai', 'done': True})}\n\n"
            except Exception as e:
                # Log the error with detailed information
                logger.error(f"Failed to call OpenAI API: {str(e)}")
                logger.exception("Exception details:")
                
                # Send error message and close the stream properly
                error_msg = f"Error: {str(e)}"
                yield f"data: {json.dumps({'content': error_msg, 'model': 'openai', 'error': True})}\n\n"
                yield f"data: {json.dumps({'content': '', 'model': 'openai', 'done': True})}\n\n"
        
        return StreamingResponse(stream_response_generator(), media_type="text/event-stream")
    else:
        # For non-streaming, return the response directly
        return await get_openai_response(messages, api_key, language)

# Grok API functions
@api_error_handler("grok")
async def stream_grok_response(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Streaming version of the Grok API call"""
    async for chunk in stream_llm_response("grok", messages, api_key, language):
        yield chunk

@api_error_handler("grok")
async def get_grok_response(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Non-streaming version of the Grok API call"""
    return await get_llm_response("grok", messages, api_key, language)

@api_error_handler("grok")
async def call_grok(messages: List[Dict[str, str]], api_key: str = None, use_streaming: bool = False, language: str = "en"):
    """Direct implementation of Grok API call with streaming support"""
    if use_streaming:
        # For streaming, implement the streaming logic directly here
        # Get the API key and model name
        key_to_use = api_key or get_api_key("grok")
        model_name = get_model("grok")
        
        # Define the streaming response generator
        async def stream_response_generator():
            try:
                # Get the client
                client = get_grok_client(key_to_use)
                
                # Make the API call directly
                response = await client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    stream=True
                )
                
                # Process the streaming response
                async for chunk in response:
                    if hasattr(chunk, 'choices') and chunk.choices and hasattr(chunk.choices[0], 'delta'):
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            content = delta.content
                            yield f"data: {json.dumps({'content': content, 'model': 'grok'})}\n\n"
                
                # Send a final empty data message to properly close the stream
                yield f"data: {json.dumps({'content': '', 'model': 'grok', 'done': True})}\n\n"
            except Exception as e:
                # Log the error with detailed information
                logger.error(f"Failed to call Grok API: {str(e)}")
                logger.exception("Exception details:")
                
                # Send error message and close the stream properly
                error_msg = f"Error: {str(e)}"
                yield f"data: {json.dumps({'content': error_msg, 'model': 'grok', 'error': True})}\n\n"
                yield f"data: {json.dumps({'content': '', 'model': 'grok', 'done': True})}\n\n"
        
        return StreamingResponse(stream_response_generator(), media_type="text/event-stream")
    else:
        # For non-streaming, return the response directly
        return await get_grok_response(messages, api_key, language)

# Qwen API functions
@api_error_handler("qwen")
async def stream_qwen_response(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Streaming version of the Qwen API call"""
    async for chunk in stream_llm_response("qwen", messages, api_key, language):
        yield chunk

@api_error_handler("qwen")
async def get_qwen_response(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Non-streaming version of the Qwen API call"""
    return await get_llm_response("qwen", messages, api_key, language)

@api_error_handler("qwen")
async def call_qwen(messages: List[Dict[str, str]], api_key: str = None, use_streaming: bool = False, language: str = "en"):
    """Direct implementation of Qwen API call with streaming support"""
    if use_streaming:
        # For streaming, implement the streaming logic directly here
        # Get the API key and model name
        key_to_use = api_key or get_api_key("qwen")
        model_name = get_model("qwen")
        
        # Define the streaming response generator
        async def stream_response_generator():
            try:
                # Get the client
                client = get_qwen_client(key_to_use)
                
                # Make the API call directly
                response = await client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    stream=True
                )
                
                # Process the streaming response
                async for chunk in response:
                    if hasattr(chunk, 'choices') and chunk.choices and hasattr(chunk.choices[0], 'delta'):
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            content = delta.content
                            yield f"data: {json.dumps({'content': content, 'model': 'qwen'})}\n\n"
                
                # Send a final empty data message to properly close the stream
                yield f"data: {json.dumps({'content': '', 'model': 'qwen', 'done': True})}\n\n"
            except Exception as e:
                # Log the error with detailed information
                logger.error(f"Failed to call Qwen API: {str(e)}")
                logger.exception("Exception details:")
                
                # Send error message and close the stream properly
                error_msg = f"Error: {str(e)}"
                yield f"data: {json.dumps({'content': error_msg, 'model': 'qwen', 'error': True})}\n\n"
                yield f"data: {json.dumps({'content': '', 'model': 'qwen', 'done': True})}\n\n"
        
        return StreamingResponse(stream_response_generator(), media_type="text/event-stream")
    else:
        # For non-streaming, return the response directly
        return await get_qwen_response(messages, api_key, language)

# DeepSeek API functions
@api_error_handler("deepseek")
async def stream_deepseek_response(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Streaming version of the DeepSeek API call"""
    async for chunk in stream_llm_response("deepseek", messages, api_key, language):
        yield chunk

@api_error_handler("deepseek")
async def get_deepseek_response(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Non-streaming version of the DeepSeek API call"""
    return await get_llm_response("deepseek", messages, api_key, language)

# DeepSeek implementation moved to a single location below (around line 585)        return await get_deepseek_response(messages, api_key, language)

# GLM API functions
@api_error_handler("glm")
async def stream_glm_response(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Streaming version of the GLM API call"""
    async for chunk in stream_llm_response("glm", messages, api_key, language):
        yield chunk

@api_error_handler("glm")
async def get_glm_response(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Non-streaming version of the GLM API call"""
    return await get_llm_response("glm", messages, api_key, language)

# GLM implementation moved to a single location below (around line 570)

# Doubao API functions
@api_error_handler("doubao")
async def stream_doubao_response(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Streaming version of the Doubao API call"""
    async for chunk in stream_llm_response("doubao", messages, api_key, language):
        yield chunk

@api_error_handler("doubao")
async def get_doubao_response(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Non-streaming version of the Doubao API call"""
    return await get_llm_response("doubao", messages, api_key, language)

@api_error_handler("doubao")
async def call_doubao(messages: List[Dict[str, str]], api_key: str = None, use_streaming: bool = False, language: str = "en"):
    """Direct implementation of Doubao API call with streaming support"""
    if use_streaming:
        # For streaming, implement the streaming logic directly here
        # Get the API key and model name
        key_to_use = api_key or get_api_key("doubao")
        model_name = get_model("doubao")
        
        # Define the streaming response generator
        async def stream_response_generator():
            try:
                # Get the client
                client = get_doubao_client(key_to_use)
                
                # Make the API call directly
                response = await client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    stream=True
                )
                
                # Process the streaming response
                async for chunk in response:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        yield f"data: {json.dumps({'content': content, 'model': 'doubao'})}\n\n"
                
                # Send a final empty data message to properly close the stream
                yield f"data: {json.dumps({'content': '', 'model': 'doubao', 'done': True})}\n\n"
            except Exception as e:
                # Log the error
                logger.error(f"Failed to call Doubao API: {str(e)}")
                logger.exception("Exception details:")
                
                # Send error message and close the stream properly
                error_msg = f"Error: {str(e)}"
                yield f"data: {json.dumps({'content': error_msg, 'model': 'doubao', 'error': True})}\n\n"
                yield f"data: {json.dumps({'content': '', 'model': 'doubao', 'done': True})}\n\n"
        
        return StreamingResponse(stream_response_generator(), media_type="text/event-stream")
    else:
        # For non-streaming, return the response directly
        return await get_doubao_response(messages, api_key, language)

@api_error_handler("glm")
async def call_glm(messages: List[Dict[str, str]], api_key: str = None, use_streaming: bool = False, language: str = "en"):
    """Direct implementation of GLM API call with streaming support"""
    if use_streaming:
        # For streaming, implement the streaming logic directly here
        # Get the API key and model name
        key_to_use = api_key or get_api_key("glm")
        model_name = get_model("glm")
        
        # Define the streaming response generator
        async def stream_response_generator():
            try:
                # Get the client
                client = get_glm_client(key_to_use)
                
                # Make the API call directly
                response = await client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    stream=True
                )
                
                # Process the streaming response directly without decoding
                # This avoids the 'str' object has no attribute 'decode' error
                async for chunk in response:
                    # Check if the chunk has content and handle it directly as a string
                    if hasattr(chunk, 'choices') and chunk.choices and hasattr(chunk.choices[0], 'delta'):
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            content = delta.content
                            # Format as SSE event directly
                            yield f"data: {json.dumps({'content': content, 'model': 'glm'})}\n\n"
                
                # Send a final empty data message to properly close the stream
                yield f"data: {json.dumps({'content': '', 'model': 'glm', 'done': True})}\n\n"
            except Exception as e:
                # Log the error with detailed information
                logger.error(f"Failed to call GLM API: {str(e)}")
                logger.exception("Exception details:")
                
                # Send error message and close the stream properly
                error_msg = f"Error: {str(e)}"
                yield f"data: {json.dumps({'content': error_msg, 'model': 'glm', 'error': True})}\n\n"
                yield f"data: {json.dumps({'content': '', 'model': 'glm', 'done': True})}\n\n"
        
        return StreamingResponse(stream_response_generator(), media_type="text/event-stream")
    else:
        # For non-streaming, return the response directly
        return await get_glm_response(messages, api_key, language)

@api_error_handler("deepseek")
async def get_deepseek_response(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Non-streaming version of the DeepSeek API call"""
    return await get_llm_response("deepseek", messages, api_key, language)

@api_error_handler("deepseek")
async def call_deepseek(messages: List[Dict[str, str]], api_key: str = None, use_streaming: bool = False, language: str = "en"):
    """Direct implementation of DeepSeek API call with streaming support"""
    if use_streaming:
        # For streaming, implement the streaming logic directly here
        # Get the API key and model name
        key_to_use = api_key or get_api_key("deepseek")
        model_name = get_model("deepseek")
        
        # Define the streaming response generator
        async def stream_response_generator():
            try:
                # Get the client
                client = get_deepseek_client(key_to_use)
                
                # Make the API call directly
                response = await client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    stream=True
                )
                
                # Process the streaming response
                async for chunk in response:
                    if hasattr(chunk, 'choices') and chunk.choices and hasattr(chunk.choices[0], 'delta'):
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            content = delta.content
                            yield f"data: {json.dumps({'content': content, 'model': 'deepseek'})}\n\n"
                
                # Send a final empty data message to properly close the stream
                yield f"data: {json.dumps({'content': '', 'model': 'deepseek', 'done': True})}\n\n"
            except Exception as e:
                # Log the error with detailed information
                logger.error(f"Failed to call DeepSeek API: {str(e)}")
                logger.exception("Exception details:")
                
                # Send error message and close the stream properly
                error_msg = f"Error: {str(e)}"
                yield f"data: {json.dumps({'content': error_msg, 'model': 'deepseek', 'error': True})}\n\n"
                yield f"data: {json.dumps({'content': '', 'model': 'deepseek', 'done': True})}\n\n"
        
        return StreamingResponse(stream_response_generator(), media_type="text/event-stream")
    else:
        # For non-streaming, return the response directly
        return await get_deepseek_response(messages, api_key, language)

async def generate_summary(responses: Dict[str, str], question: str, api_key: str = None, language: str = "en", use_streaming: bool = False):
    """
    Generate a summary of responses from multiple models.
    
    Args:
        responses: Dictionary mapping model names to their responses
        question: The original question asked
        api_key: Optional API key to use (overrides environment variable)
        language: Language code for the summary (en or zh)
        
    Returns:
        Summary text comparing the different model responses
        
    Raises:
        HTTPException: If all API calls fail
    """
    # Format the summary prompt using the template
    prompt = get_summary_prompt(question, responses, language)
    
    # Determine which model to use for the summary based on language
    summary_model = "qwen" if language == "zh" else "openai"
    
    # Get the correct 'call_X' function based on the model name
    model_call_function = None
    if summary_model == "openai":
        model_call_function = call_openai
    elif summary_model == "grok":
        model_call_function = call_grok
    elif summary_model == "qwen":
        model_call_function = call_qwen
    elif summary_model == "deepseek":
        model_call_function = call_deepseek
    elif summary_model == "glm":
        model_call_function = call_glm
    elif summary_model == "doubao":
        model_call_function = call_doubao
    else:
        raise ValueError(f"Unsupported summary model: {summary_model}")
        
    # Make sure we have a call function
    if not model_call_function:
        raise HTTPException(status_code=500, detail="Could not determine summary model function")
    
    # Call the model with the formatted prompt
    system_prompt = {
        "role": "system",
        "content": "You are a helpful AI assistant tasked with comparing responses from different AI models. Your job is to create a concise, clear summary table highlighting similarities and differences between the responses."
    }
    
    user_prompt = {
        "role": "user",
        "content": prompt
    }
    
    try:
        result = await model_call_function([system_prompt, user_prompt], api_key, use_streaming=use_streaming, language=language)
        
        if use_streaming:
            # For streaming, return the generator
            return result
        else:
            # For non-streaming, return the content
            return {"content": result.get("content", "")}
            
    except Exception as e:
        logger.error(f"Summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")
