from fastapi import HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import Dict, List, Optional, Any, Callable, AsyncGenerator
import httpx
import time
import random
import os
import sys
import json
from openai import AsyncOpenAI
import asyncio

# Add the parent directory to path to support both running methods
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Try relative imports first, then fall back to absolute imports
try:
    # For running from backend directory
    from ..env_config import get_api_key, get_api_url, get_model
    from .summary_prompts import get_summary_prompt
    from .logger import logger
except (ImportError, ValueError):
    # For running from project root with module prefix
    from backend.env_config import get_api_key, get_api_url, get_model
    from backend.utils.summary_prompts import get_summary_prompt
    from backend.utils.logger import logger

# Default timeout for API calls (in seconds)
DEFAULT_TIMEOUT = 60.0
MAX_RETRIES_COUNT = 6

# Shared clients for APIs
_openai_client = None   # OpenAI SDK client
_glm_client = None      # OpenAI-compatible client for GLM
_doubao_client = None   # OpenAI-compatible client for Doubao
_grok_client = None     # OpenAI-compatible client for Grok
_qwen_client = None     # OpenAI-compatible client for Qwen
_deepseek_client = None # OpenAI-compatible client for DeepSeek
_httpx_client = None    # httpx client for HTTP-based APIs (legacy)

def get_openai_client(api_key: str = None) -> AsyncOpenAI:
    """
    Get or create a shared OpenAI client with the specified API key.
    
    Args:
        api_key: Optional API key to use, defaults to environment variable
        
    Returns:
        AsyncOpenAI client instance
    """
    global _openai_client
    
    # Use user-provided key if available, otherwise use environment variable
    key_to_use = api_key or get_api_key("openai")
    
    if not key_to_use:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
    # Create a new client if we don't have one or if the API key is different
    if _openai_client is None or _openai_client.api_key != key_to_use:
        _openai_client = AsyncOpenAI(
            api_key=key_to_use,
            max_retries=MAX_RETRIES_COUNT,
            timeout=DEFAULT_TIMEOUT
        )
    
    return _openai_client

def get_glm_client(api_key: str = None) -> AsyncOpenAI:
    """
    Get or create a shared GLM client with the specified API key.
    
    Args:
        api_key: Optional API key to use, defaults to environment variable
        
    Returns:
        AsyncOpenAI client instance configured for GLM API
    """
    global _glm_client
    
    # Use user-provided key if available, otherwise use environment variable
    key_to_use = api_key or get_api_key("glm")
    
    if not key_to_use:
        raise HTTPException(status_code=500, detail="GLM API key not configured")
    
    api_url = get_api_url("glm")
    
    # Create a new client if we don't have one or if the API key is different
    if _glm_client is None or _glm_client.api_key != key_to_use:
        _glm_client = AsyncOpenAI(
            api_key=key_to_use,
            base_url=api_url,
            max_retries=MAX_RETRIES_COUNT,
            timeout=DEFAULT_TIMEOUT
        )
    
    return _glm_client

def get_doubao_client(api_key: str = None) -> AsyncOpenAI:
    """
    Get or create a shared Doubao client with the specified API key.
    
    Args:
        api_key: Optional API key to use, defaults to environment variable
        
    Returns:
        AsyncOpenAI client instance configured for Doubao API
    """
    global _doubao_client
    
    # Use user-provided key if available, otherwise use environment variable
    key_to_use = api_key or get_api_key("doubao")
    
    if not key_to_use:
        raise HTTPException(status_code=500, detail="Doubao API key not configured")
    
    api_url = get_api_url("doubao")
    
    # Create a new client if we don't have one or if the API key is different
    if _doubao_client is None or _doubao_client.api_key != key_to_use:
        _doubao_client = AsyncOpenAI(
            api_key=key_to_use,
            base_url=api_url,
            max_retries=MAX_RETRIES_COUNT,
            timeout=DEFAULT_TIMEOUT
        )
    
    return _doubao_client

def get_grok_client(api_key: str = None) -> AsyncOpenAI:
    """
    Get or create a shared Grok client with the specified API key.
    
    Args:
        api_key: Optional API key to use, defaults to environment variable
        
    Returns:
        AsyncOpenAI client instance configured for Grok API
    """
    global _grok_client
    
    # Use user-provided key if available, otherwise use environment variable
    key_to_use = api_key or get_api_key("grok")
    
    if not key_to_use:
        raise HTTPException(status_code=500, detail="Grok API key not configured")
    
    api_url = get_api_url("grok")
    
    # Create a new client if we don't have one or if the API key is different
    if _grok_client is None or _grok_client.api_key != key_to_use:
        _grok_client = AsyncOpenAI(
            api_key=key_to_use,
            base_url=api_url,
            max_retries=MAX_RETRIES_COUNT,
            timeout=DEFAULT_TIMEOUT
        )
    
    return _grok_client

def get_qwen_client(api_key: str = None) -> AsyncOpenAI:
    """
    Get or create a shared Qwen client with the specified API key.
    
    Args:
        api_key: Optional API key to use, defaults to environment variable
        
    Returns:
        AsyncOpenAI client instance configured for Qwen API
    """
    global _qwen_client
    
    # Use user-provided key if available, otherwise use environment variable
    key_to_use = api_key or get_api_key("qwen")
    
    if not key_to_use:
        raise HTTPException(status_code=500, detail="Qwen API key not configured")
    
    api_url = get_api_url("qwen")
    
    # Create a new client if we don't have one or if the API key is different
    if _qwen_client is None or _qwen_client.api_key != key_to_use:
        _qwen_client = AsyncOpenAI(
            api_key=key_to_use,
            base_url=api_url,
            max_retries=MAX_RETRIES_COUNT,
            timeout=DEFAULT_TIMEOUT
        )
    
    return _qwen_client

def get_deepseek_client(api_key: str = None) -> AsyncOpenAI:
    """
    Get or create a shared DeepSeek client with the specified API key.
    
    Args:
        api_key: Optional API key to use, defaults to environment variable
        
    Returns:
        AsyncOpenAI client instance configured for DeepSeek API
    """
    global _deepseek_client
    
    # Use user-provided key if available, otherwise use environment variable
    key_to_use = api_key or get_api_key("deepseek")
    
    if not key_to_use:
        raise HTTPException(status_code=500, detail="DeepSeek API key not configured")
    
    api_url = get_api_url("deepseek")
    
    # Create a new client if we don't have one or if the API key is different
    if _deepseek_client is None or _deepseek_client.api_key != key_to_use:
        _deepseek_client = AsyncOpenAI(
            api_key=key_to_use,
            base_url=api_url,
            max_retries=MAX_RETRIES_COUNT,
            timeout=DEFAULT_TIMEOUT
        )
    
    return _deepseek_client

def get_httpx_client() -> httpx.AsyncClient:
    """
    Get or create a shared httpx client for HTTP-based APIs.
    
    Returns:
        httpx.AsyncClient instance with configured timeout
    """
    global _httpx_client
    
    if _httpx_client is None or _httpx_client.is_closed:
        _httpx_client = httpx.AsyncClient(timeout=httpx.Timeout(DEFAULT_TIMEOUT))
    
    return _httpx_client

# Helper function to decode API key from header
def decode_api_key(req: Request, header_name: str) -> Optional[str]:
    from urllib.parse import unquote
    api_key = req.headers.get(header_name)
    if api_key:
        return unquote(api_key)
    return None

# Helper functions for API calls
async def call_openai_stream(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Streaming version of the OpenAI API call"""
    try:
        client = get_openai_client(api_key)
        model_name = get_model("openai")
        
        response_stream = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True
        )
        
        # For a streaming response, yield only the delta content
        async for chunk in response_stream:
            if chunk.choices[0].delta.content is not None:
                delta = chunk.choices[0].delta.content
                yield delta
        return  # Exit the generator when done
    except Exception as e:
        logger.error(f"Failed to call OpenAI API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

async def call_openai_no_stream(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Non-streaming version of the OpenAI API call"""
    try:
        client = get_openai_client(api_key)
        model_name = get_model("openai")
        
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=False
        )
        return {"content": response.choices[0].message.content}
    except Exception as e:
        logger.error(f"Failed to call OpenAI API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

async def call_openai(messages: List[Dict[str, str]], api_key: str = None, stream: bool = False, language: str = "en"):
    """Function that determines whether to use streaming or non-streaming version"""
    try:
        if stream:
            # For streaming, we need to wrap the generator in a StreamingResponse
            response_stream = call_openai_stream(messages, api_key, language)
            
            async def event_generator():
                async for delta in response_stream:
                    yield f"data: {json.dumps({'content': delta, 'model': 'openai'})}\n\n"
            
            return StreamingResponse(event_generator(), media_type="text/event-stream")
        else:
            # For non-streaming, return the response directly
            return await call_openai_no_stream(messages, api_key, language)
    except Exception as e:
        logger.error(f"Failed to call OpenAI API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

async def call_grok_stream(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Streaming version of the Grok API call"""
    try:
        client = get_grok_client(api_key)
        model_name = get_model("grok")
        
        response_stream = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True
        )
        
        # For a streaming response, yield only the delta content
        async for chunk in response_stream:
            if chunk.choices[0].delta.content is not None:
                delta = chunk.choices[0].delta.content
                yield delta
        return  # Exit the generator when done
    except Exception as e:
        logger.error(f"Failed to call Grok API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Grok API error: {str(e)}")

async def call_grok_no_stream(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Non-streaming version of the Grok API call"""
    try:
        client = get_grok_client(api_key)
        model_name = get_model("grok")
        
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages
        )
        
        return {"content": response.choices[0].message.content}
    except Exception as e:
        logger.error(f"Failed to call Grok API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Grok API error: {str(e)}")

async def call_grok(messages: List[Dict[str, str]], api_key: str = None, stream: bool = False, language: str = "en"):
    """Function that determines whether to use streaming or non-streaming version"""
    try:
        if stream:
            # For streaming, we need to wrap the generator in a StreamingResponse
            response_stream = call_grok_stream(messages, api_key, language)
            
            async def event_generator():
                async for delta in response_stream:
                    yield f"data: {json.dumps({'content': delta, 'model': 'grok'})}\n\n"
            
            return StreamingResponse(event_generator(), media_type="text/event-stream")
        else:
            # For non-streaming, return the response directly
            return await call_grok_no_stream(messages, api_key, language)
    except Exception as e:
        logger.error(f"Failed to call Grok API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Grok API error: {str(e)}")

async def call_qwen_stream(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Streaming version of the Qwen API call"""
    try:
        client = get_qwen_client(api_key)
        model_name = get_model("qwen")
        
        response_stream = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True
        )
        
        # For a streaming response, yield only the delta content
        async for chunk in response_stream:
            if chunk.choices[0].delta.content is not None:
                delta = chunk.choices[0].delta.content
                yield delta
        return  # Exit the generator when done
    except Exception as e:
        logger.error(f"Failed to call Qwen API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Qwen API error: {str(e)}")

async def call_qwen_no_stream(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Non-streaming version of the Qwen API call"""
    try:
        client = get_qwen_client(api_key)
        model_name = get_model("qwen")
        
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages
        )
        
        return {"content": response.choices[0].message.content}
    except Exception as e:
        logger.error(f"Failed to call Qwen API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Qwen API error: {str(e)}")

async def call_qwen(messages: List[Dict[str, str]], api_key: str = None, stream: bool = False, language: str = "en"):
    """Function that determines whether to use streaming or non-streaming version"""
    try:
        if stream:
            # For streaming, we need to wrap the generator in a StreamingResponse
            response_stream = call_qwen_stream(messages, api_key, language)
            
            async def event_generator():
                async for delta in response_stream:
                    yield f"data: {json.dumps({'content': delta, 'model': 'qwen'})}\n\n"
            
            return StreamingResponse(event_generator(), media_type="text/event-stream")
        else:
            # For non-streaming, return the response directly
            return await call_qwen_no_stream(messages, api_key, language)
    except Exception as e:
        logger.error(f"Failed to call Qwen API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Qwen API error: {str(e)}")

async def call_deepseek_stream(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Streaming version of the DeepSeek API call"""
    try:
        client = get_deepseek_client(api_key)
        model_name = get_model("deepseek")
        
        response_stream = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True
        )
        
        # For a streaming response, yield only the delta content
        async for chunk in response_stream:
            if chunk.choices[0].delta.content is not None:
                delta = chunk.choices[0].delta.content
                yield delta
        return  # Exit the generator when done
    except Exception as e:
        logger.error(f"Failed to call DeepSeek API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"DeepSeek API error: {str(e)}")

async def call_deepseek_no_stream(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Non-streaming version of the DeepSeek API call"""
    try:
        client = get_deepseek_client(api_key)
        model_name = get_model("deepseek")
        
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages
        )
        
        return {"content": response.choices[0].message.content}
    except Exception as e:
        logger.error(f"Failed to call DeepSeek API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"DeepSeek API error: {str(e)}")

async def call_deepseek(messages: List[Dict[str, str]], api_key: str = None, stream: bool = False, language: str = "en"):
    """Function that determines whether to use streaming or non-streaming version"""
    try:
        if stream:
            # For streaming, we need to wrap the generator in a StreamingResponse
            response_stream = call_deepseek_stream(messages, api_key, language)
            
            async def event_generator():
                async for delta in response_stream:
                    yield f"data: {json.dumps({'content': delta, 'model': 'deepseek'})}\n\n"
            
            return StreamingResponse(event_generator(), media_type="text/event-stream")
        else:
            # For non-streaming, return the response directly
            return await call_deepseek_no_stream(messages, api_key, language)
    except Exception as e:
        logger.error(f"Failed to call DeepSeek API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"DeepSeek API error: {str(e)}")

async def call_glm_stream(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Streaming version of the GLM API call"""
    try:
        client = get_glm_client(api_key)
        model_name = get_model("glm")
        
        response_stream = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True
        )
        
        # For a streaming response, yield only the delta content
        async for chunk in response_stream:
            if chunk.choices[0].delta.content is not None:
                delta = chunk.choices[0].delta.content
                yield delta
        return  # Exit the generator when done
    except Exception as e:
        logger.error(f"Failed to call GLM API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"GLM API error: {str(e)}")

async def call_glm_no_stream(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Non-streaming version of the GLM API call"""
    try:
        client = get_glm_client(api_key)
        model_name = get_model("glm")
        
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=False
        )
        return {"content": response.choices[0].message.content}
    except Exception as e:
        logger.error(f"Failed to call GLM API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"GLM API error: {str(e)}")

async def call_glm(messages: List[Dict[str, str]], api_key: str = None, stream: bool = False, language: str = "en"):
    """Function that determines whether to use streaming or non-streaming version"""
    try:
        if stream:
            # For streaming, we need to wrap the generator in a StreamingResponse
            response_stream = call_glm_stream(messages, api_key, language)
            
            async def event_generator():
                async for delta in response_stream:
                    yield f"data: {json.dumps({'content': delta, 'model': 'glm'})}\n\n"
            
            return StreamingResponse(event_generator(), media_type="text/event-stream")
        else:
            # For non-streaming, return the response directly
            return await call_glm_no_stream(messages, api_key, language)
    except Exception as e:
        logger.error(f"Failed to call GLM API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"GLM API error: {str(e)}")

async def call_doubao_stream(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Streaming version of the Doubao API call"""
    try:
        client = get_doubao_client(api_key)
        model_name = get_model("doubao")
        
        response_stream = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True
        )
        
        # For a streaming response, yield only the delta content
        async for chunk in response_stream:
            if chunk.choices[0].delta.content is not None:
                delta = chunk.choices[0].delta.content
                yield delta
        return  # Exit the generator when done
    except Exception as e:
        logger.error(f"Failed to call Doubao API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Doubao API error: {str(e)}")

async def call_doubao_no_stream(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Non-streaming version of the Doubao API call"""
    try:
        client = get_doubao_client(api_key)
        model_name = get_model("doubao")
        
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=False
        )
        return {"content": response.choices[0].message.content}
    except Exception as e:
        logger.error(f"Failed to call Doubao API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Doubao API error: {str(e)}")

async def call_doubao(messages: List[Dict[str, str]], api_key: str = None, stream: bool = False, language: str = "en"):
    """Function that determines whether to use streaming or non-streaming version"""
    try:
        if stream:
            # For streaming, we need to wrap the generator in a StreamingResponse
            response_stream = call_doubao_stream(messages, api_key, language)
            
            async def event_generator():
                async for delta in response_stream:
                    yield f"data: {json.dumps({'content': delta, 'model': 'doubao'})}\n\n"
            
            return StreamingResponse(event_generator(), media_type="text/event-stream")
        else:
            # For non-streaming, return the response directly
            return await call_doubao_no_stream(messages, api_key, language)
    except Exception as e:
        logger.error(f"Failed to call Doubao API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Doubao API error: {str(e)}")

async def generate_summary(responses: Dict[str, str], question: str, api_key: str = None, language: str = "en", stream: bool = False):
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
        result = await model_call_function([system_prompt, user_prompt], api_key, stream=stream, language=language)
        
        if stream:
            # For streaming, return the generator
            return result
        else:
            # For non-streaming, return the content
            return {"content": result.get("content", "")}
            
    except Exception as e:
        logger.error(f"Summary generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")
