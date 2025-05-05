"""
Direct implementation of streaming API calls without complex nesting.
This file provides simplified implementations that avoid the 'coroutine was never awaited' warnings.
"""
import asyncio
import json
import os
import sys
from typing import AsyncGenerator, Dict, List, Optional

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the necessary modules from the backend
from backend.env_config import get_api_key, get_api_url, get_model
from backend.utils.model_helpers import (get_deepseek_client,
                                         get_doubao_client, get_glm_client,
                                         get_grok_client, get_openai_client,
                                         get_qwen_client)


# Direct implementation of OpenAI streaming
async def direct_openai_stream(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Direct implementation of OpenAI streaming without nested async generators"""
    try:
        # Get the API key and model name
        key_to_use = api_key or get_api_key("openai")
        model_name = get_model("openai")
        
        # Get the client
        client = get_openai_client(key_to_use)
        
        # Make the API call directly
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True
        )
        
        # Create the event generator
        async def event_generator():
            try:
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
                # Send error message and close the stream properly
                error_msg = f"Error: {str(e)}"
                yield f"data: {json.dumps({'content': error_msg, 'model': 'openai', 'error': True})}\n\n"
                yield f"data: {json.dumps({'content': '', 'model': 'openai', 'done': True})}\n\n"
        
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        # Handle any exceptions that occur during the API call
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

# Direct implementation of GLM streaming
async def direct_glm_stream(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Direct implementation of GLM streaming without nested async generators"""
    try:
        # Get the API key and model name
        key_to_use = api_key or get_api_key("glm")
        model_name = get_model("glm")
        
        # Get the client
        client = get_glm_client(key_to_use)
        
        # Make the API call directly
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True
        )
        
        # Create the event generator
        async def event_generator():
            try:
                # Process the streaming response
                async for chunk in response:
                    if hasattr(chunk, 'choices') and chunk.choices and hasattr(chunk.choices[0], 'delta'):
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            content = delta.content
                            yield f"data: {json.dumps({'content': content, 'model': 'glm'})}\n\n"
                
                # Send a final empty data message to properly close the stream
                yield f"data: {json.dumps({'content': '', 'model': 'glm', 'done': True})}\n\n"
            except Exception as e:
                # Send error message and close the stream properly
                error_msg = f"Error: {str(e)}"
                yield f"data: {json.dumps({'content': error_msg, 'model': 'glm', 'error': True})}\n\n"
                yield f"data: {json.dumps({'content': '', 'model': 'glm', 'done': True})}\n\n"
        
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        # Handle any exceptions that occur during the API call
        raise HTTPException(status_code=500, detail=f"GLM API error: {str(e)}")

# Direct implementation of Doubao streaming
async def direct_doubao_stream(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Direct implementation of Doubao streaming without nested async generators"""
    try:
        # Get the API key and model name
        key_to_use = api_key or get_api_key("doubao")
        model_name = get_model("doubao")
        
        # Get the client
        client = get_doubao_client(key_to_use)
        
        # Make the API call directly
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True
        )
        
        # Create the event generator
        async def event_generator():
            try:
                # Process the streaming response
                async for chunk in response:
                    if hasattr(chunk, 'choices') and chunk.choices and hasattr(chunk.choices[0], 'delta'):
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            content = delta.content
                            yield f"data: {json.dumps({'content': content, 'model': 'doubao'})}\n\n"
                
                # Send a final empty data message to properly close the stream
                yield f"data: {json.dumps({'content': '', 'model': 'doubao', 'done': True})}\n\n"
            except Exception as e:
                # Send error message and close the stream properly
                error_msg = f"Error: {str(e)}"
                yield f"data: {json.dumps({'content': error_msg, 'model': 'doubao', 'error': True})}\n\n"
                yield f"data: {json.dumps({'content': '', 'model': 'doubao', 'done': True})}\n\n"
        
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        # Handle any exceptions that occur during the API call
        raise HTTPException(status_code=500, detail=f"Doubao API error: {str(e)}")

# Direct implementation of Grok streaming
async def direct_grok_stream(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Direct implementation of Grok streaming without nested async generators"""
    try:
        # Get the API key and model name
        key_to_use = api_key or get_api_key("grok")
        model_name = get_model("grok")
        
        # Get the client
        client = get_grok_client(key_to_use)
        
        # Make the API call directly
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True
        )
        
        # Create the event generator
        async def event_generator():
            try:
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
                # Send error message and close the stream properly
                error_msg = f"Error: {str(e)}"
                yield f"data: {json.dumps({'content': error_msg, 'model': 'grok', 'error': True})}\n\n"
                yield f"data: {json.dumps({'content': '', 'model': 'grok', 'done': True})}\n\n"
        
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        # Handle any exceptions that occur during the API call
        raise HTTPException(status_code=500, detail=f"Grok API error: {str(e)}")

# Direct implementation of Qwen streaming
async def direct_qwen_stream(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Direct implementation of Qwen streaming without nested async generators"""
    try:
        # Get the API key and model name
        key_to_use = api_key or get_api_key("qwen")
        model_name = get_model("qwen")
        
        # Get the client
        client = get_qwen_client(key_to_use)
        
        # Make the API call directly
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True
        )
        
        # Create the event generator
        async def event_generator():
            try:
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
                # Send error message and close the stream properly
                error_msg = f"Error: {str(e)}"
                yield f"data: {json.dumps({'content': error_msg, 'model': 'qwen', 'error': True})}\n\n"
                yield f"data: {json.dumps({'content': '', 'model': 'qwen', 'done': True})}\n\n"
        
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        # Handle any exceptions that occur during the API call
        raise HTTPException(status_code=500, detail=f"Qwen API error: {str(e)}")

# Direct implementation of DeepSeek streaming
async def direct_deepseek_stream(messages: List[Dict[str, str]], api_key: str = None, language: str = "en"):
    """Direct implementation of DeepSeek streaming without nested async generators"""
    try:
        # Get the API key and model name
        key_to_use = api_key or get_api_key("deepseek")
        model_name = get_model("deepseek")
        
        # Get the client
        client = get_deepseek_client(key_to_use)
        
        # Make the API call directly
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True
        )
        
        # Create the event generator
        async def event_generator():
            try:
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
                # Send error message and close the stream properly
                error_msg = f"Error: {str(e)}"
                yield f"data: {json.dumps({'content': error_msg, 'model': 'deepseek', 'error': True})}\n\n"
                yield f"data: {json.dumps({'content': '', 'model': 'deepseek', 'done': True})}\n\n"
        
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        # Handle any exceptions that occur during the API call
        raise HTTPException(status_code=500, detail=f"DeepSeek API error: {str(e)}")
