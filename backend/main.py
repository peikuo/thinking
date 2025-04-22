from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import httpx
import os
import asyncio
import json
import time
from openai import AsyncOpenAI

# Import environment-based configuration module
from env_config import (
    get_api_key, get_api_url, get_model, get_server_config,
    get_current_env, switch_environment, get_log_level,
    ENV_DEV, ENV_TEST, ENV_PRD
)

# Import custom logging and middleware
from utils.logger import logger, archive_old_logs
from utils.middleware import RequestLoggingMiddleware
from utils.model_prompts import get_model_prompt, get_summary_prompt

app = FastAPI(title="Thinking API", description="API for the Thinking project")

# CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, in production specify the actual origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Initialize logging system
logger.info(f"Starting Thinking API in {get_current_env()} environment with log level {get_log_level()}")

# Archive old logs on startup
try:
    archive_old_logs()
    logger.info("Successfully archived old logs")
except Exception as e:
    logger.warning(f"Failed to archive old logs: {str(e)}")

# Get API keys and URLs from configuration
OPENAI_API_KEY = get_api_key("openai")
GROK_API_KEY = get_api_key("grok")
QWEN_API_KEY = get_api_key("qwen")
DEEPSEEK_API_KEY = get_api_key("deepseek")
GLM_API_KEY = get_api_key("glm")
GLM_API_URL = get_api_url("glm")
DOUBAO_API_KEY = get_api_key("doubao")
DOUBAO_API_URL = get_api_url("doubao")

# API endpoints
OPENAI_API_URL = get_api_url("openai")
GROK_API_URL = get_api_url("grok")
QWEN_API_URL = get_api_url("qwen")
DEEPSEEK_API_URL = get_api_url("deepseek")

# Default timeout for API calls (in seconds)
DEFAULT_TIMEOUT = 60.0
MAX_RETRIES_COUNT = 6

# Request models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    language: Optional[str] = "en"
    stream: Optional[bool] = True

class SummaryRequest(BaseModel):
    responses: Dict[str, str]
    question: str
    language: Optional[str] = "en"
    stream: Optional[bool] = True

# Helper functions for API calls
async def call_openai(messages: List[Dict[str, str]], api_key: str = None, stream: bool = False, language: str = "en"):
    # Use user-provided key if available, otherwise use environment variable
    key_to_use = api_key or OPENAI_API_KEY
    
    if not key_to_use:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    # Get the system prompt for OpenAI in the specified language
    system_prompt = get_model_prompt("openai", language)
    
    # Add system prompt if not already present
    if not any(msg.get("role") == "system" for msg in messages):
        messages = [
            {"role": "system", "content": system_prompt}
        ] + messages
    
    print("openai trace: ", messages)
    try:
        # Create an OpenAI client with the API key
        client = AsyncOpenAI(
            api_key=key_to_use,
            base_url=OPENAI_API_URL,
            max_retries=MAX_RETRIES_COUNT
            # Use the default base URL for OpenAI
        )
        
        # Make the API call using the client
        if stream:
            # For streaming responses, return a StreamingResponse
            from fastapi.responses import StreamingResponse
            
            async def content_generator():
                try:
                    stream_response = await client.chat.completions.create(
                        model=get_model("openai"),
                        messages=messages,
                        stream=True,
                        timeout=DEFAULT_TIMEOUT
                    )
                    
                    # Yield each chunk as it arrives
                    async for chunk in stream_response:
                        if chunk.choices and chunk.choices[0].delta.content:
                            # No delay on backend - typing effect should be handled by frontend
                            content = chunk.choices[0].delta.content
                            yield f"data: {json.dumps({'content': content, 'model': 'openai'})}\n\n"
                    
                    # Signal the end of the stream
                    yield f"data: {json.dumps({'done': True, 'model': 'openai'})}\n\n"
                except Exception as e:
                    # Handle errors during streaming
                    yield f"data: {json.dumps({'error': str(e), 'model': 'openai'})}\n\n"
                    yield f"data: {json.dumps({'done': True, 'model': 'openai'})}\n\n"
            
            return StreamingResponse(
                content_generator(),
                media_type="text/event-stream"
            )
        else:
            # For non-streaming responses, return the full content
            response = await client.chat.completions.create(
                model=get_model("openai"),
                messages=messages,
                timeout=DEFAULT_TIMEOUT
            )
            
            # Extract and return the response content
            return response.choices[0].message.content
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Request to OpenAI API timed out. Please try again later."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI API error: {str(e)}"
        )

async def call_grok(messages: List[Dict[str, str]], api_key: str = None, stream: bool = False, language: str = "en"):
    # Use user-provided key if available, otherwise use environment variable
    key_to_use = api_key or GROK_API_KEY
    print("grok trace: ", messages)
    if not key_to_use:
        raise HTTPException(status_code=500, detail="Grok API key not configured")
    
    # Get the system prompt for Grok in the specified language
    system_prompt = get_model_prompt("grok", language)
    
    # Add system prompt for Grok
    grok_messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ] + messages
    
    try:
        # Create an OpenAI client with the API key and X.AI base URL
        client = AsyncOpenAI(
            api_key=key_to_use,
            base_url=GROK_API_URL,
            max_retries=MAX_RETRIES_COUNT
        )
        
        # Make the API call using the client
        if stream:
            # For streaming responses, return a StreamingResponse
            from fastapi.responses import StreamingResponse
            
            async def content_generator():
                try:
                    stream_response = await client.chat.completions.create(
                        model=get_model("grok"),
                        messages=grok_messages,
                        stream=True,
                        timeout=DEFAULT_TIMEOUT
                    )
                    
                    # Yield each chunk as it arrives
                    async for chunk in stream_response:
                        if chunk.choices and chunk.choices[0].delta.content:
                            # No delay on backend - typing effect should be handled by frontend
                            content = chunk.choices[0].delta.content
                            yield f"data: {json.dumps({'content': content, 'model': 'grok'})}\n\n"
                    
                    # Signal the end of the stream
                    yield f"data: {json.dumps({'done': True, 'model': 'grok'})}\n\n"
                except Exception as e:
                    # Handle errors during streaming
                    yield f"data: {json.dumps({'error': str(e), 'model': 'grok'})}\n\n"
                    yield f"data: {json.dumps({'done': True, 'model': 'grok'})}\n\n"
            
            return StreamingResponse(
                content_generator(),
                media_type="text/event-stream"
            )
        else:
            # For non-streaming responses, return the full content
            response = await client.chat.completions.create(
                model=get_model("grok"),
                messages=grok_messages,
                timeout=DEFAULT_TIMEOUT
            )
            
            # Extract and return the response content
            return response.choices[0].message.content
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Request to Grok API timed out. Please try again later."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Grok API error: {str(e)}"
        )

async def call_qwen(messages: List[Dict[str, str]], api_key: str = None, stream: bool = False, language: str = "en"):
    # Use user-provided key if available, otherwise use environment variable
    key_to_use = api_key or QWEN_API_KEY
    
    if not key_to_use:
        raise HTTPException(status_code=500, detail="Qwen API key not configured")
    
    # Get the system prompt for Qwen in the specified language
    system_prompt = get_model_prompt("qwen", language)
    
    # Convert messages to Qwen format
    prompt = f"System: {system_prompt}\n"
    for message in messages:
        if message["role"] == "user":
            prompt += f"Human: {message['content']}\n"
        elif message["role"] == "assistant":
            prompt += f"Assistant: {message['content']}\n"
        elif message["role"] == "system" and message != messages[0]:  # Skip if it's the first message (we already added our system prompt)
            prompt += f"System: {message['content']}\n"
    
    prompt += "Assistant: "
    
    try:
        # Create an OpenAI client with the API key and Qwen base URL
        client = AsyncOpenAI(
            api_key=key_to_use,
            base_url=QWEN_API_URL,
            max_retries=MAX_RETRIES_COUNT
        )
        
        # Make the API call using the client with a custom completion format
        if stream:
            # For streaming responses, return a StreamingResponse
            from fastapi.responses import StreamingResponse
            
            async def content_generator():
                try:
                    stream_response = await client.chat.completions.create(
                        model=get_model("qwen"),
                        messages=[{"role": "user", "content": prompt}],
                        stream=True,
                        timeout=DEFAULT_TIMEOUT
                    )
                    
                    # Yield each chunk as it arrives
                    async for chunk in stream_response:
                        if chunk.choices and chunk.choices[0].delta.content:
                            # No delay on backend - typing effect should be handled by frontend
                            content = chunk.choices[0].delta.content
                            yield f"data: {json.dumps({'content': content, 'model': 'qwen'})}\n\n"
                    
                    # Signal the end of the stream
                    yield f"data: {json.dumps({'done': True, 'model': 'qwen'})}\n\n"
                except Exception as e:
                    # Handle errors during streaming
                    yield f"data: {json.dumps({'error': str(e), 'model': 'qwen'})}\n\n"
                    yield f"data: {json.dumps({'done': True, 'model': 'qwen'})}\n\n"
            
            return StreamingResponse(
                content_generator(),
                media_type="text/event-stream"
            )
        else:
            # For non-streaming responses, return the full content
            response = await client.chat.completions.create(
                model=get_model("qwen"),
                messages=[{"role": "user", "content": prompt}],
                timeout=DEFAULT_TIMEOUT
            )
            
            # Extract and return the response content
            return response.choices[0].message.content
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Request to Qwen API timed out. Please try again later."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Qwen API error: {str(e)}"
        )

async def call_deepseek(messages: List[Dict[str, str]], api_key: str = None, stream: bool = False, language: str = "en"):
    # Use user-provided key if available, otherwise use environment variable
    key_to_use = api_key or DEEPSEEK_API_KEY
    
    if not key_to_use:
        raise HTTPException(status_code=500, detail="DeepSeek API key not configured")
    
    # Get the system prompt for DeepSeek in the specified language
    system_prompt = get_model_prompt("deepseek", language)
    
    # Add system prompt if not already present
    if not any(msg.get("role") == "system" for msg in messages):
        messages = [
            {"role": "system", "content": system_prompt}
        ] + messages
    
    try:
        # Create an OpenAI client with the API key and DeepSeek base URL
        client = AsyncOpenAI(
            api_key=key_to_use,
            base_url=DEEPSEEK_API_URL,
            max_retries=MAX_RETRIES_COUNT
        )
        
        # Make the API call using the client
        if stream:
            # For streaming responses, return a StreamingResponse
            from fastapi.responses import StreamingResponse
            
            async def content_generator():
                try:
                    stream_response = await client.chat.completions.create(
                        model=get_model("deepseek"),
                        messages=messages,
                        stream=True,
                        timeout=DEFAULT_TIMEOUT
                    )
                    
                    # Yield each chunk as it arrives
                    async for chunk in stream_response:
                        if chunk.choices and chunk.choices[0].delta.content:
                            # No delay on backend - typing effect should be handled by frontend
                            content = chunk.choices[0].delta.content
                            yield f"data: {json.dumps({'content': content, 'model': 'deepseek'})}\n\n"
                    
                    # Signal the end of the stream
                    yield f"data: {json.dumps({'done': True, 'model': 'deepseek'})}\n\n"
                except Exception as e:
                    # Handle errors during streaming
                    yield f"data: {json.dumps({'error': str(e), 'model': 'deepseek'})}\n\n"
                    yield f"data: {json.dumps({'done': True, 'model': 'deepseek'})}\n\n"
            
            return StreamingResponse(
                content_generator(),
                media_type="text/event-stream"
            )
        else:
            # For non-streaming responses, return the full content
            response = await client.chat.completions.create(
                model=get_model("deepseek"),
                messages=messages,
                timeout=DEFAULT_TIMEOUT
            )
            
            # Extract and return the response content
            return response.choices[0].message.content
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Request to DeepSeek API timed out. Please try again later."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"DeepSeek API error: {str(e)}"
        )

async def call_glm(messages: List[Dict[str, str]], api_key: str = None, stream: bool = False, language: str = "en"):
    """
    Call the GLM API for chat completions, using OpenAI-compatible AsyncOpenAI client, just like call_openai.
    """
    key_to_use = api_key or GLM_API_KEY
    if not key_to_use:
        raise HTTPException(status_code=500, detail="GLM API key not configured")

    # Get the system prompt for GLM in the specified language
    system_prompt = get_model_prompt("glm", language) if 'get_model_prompt' in globals() else None
    if system_prompt and not any(msg.get("role") == "system" for msg in messages):
        messages = [
            {"role": "system", "content": system_prompt}
        ] + messages

    try:
        client = AsyncOpenAI(
            api_key=key_to_use,
            base_url=GLM_API_URL,
            max_retries=MAX_RETRIES_COUNT,
        )
        if stream:
            from fastapi.responses import StreamingResponse
            async def content_generator():
                try:
                    stream_response = await client.chat.completions.create(
                        model=get_model("glm"),
                        messages=messages,
                        stream=True,
                        timeout=DEFAULT_TIMEOUT
                    )
                    async for chunk in stream_response:
                        if chunk.choices and chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            yield f"data: {json.dumps({'content': content, 'model': 'glm'})}\n\n"
                    yield f"data: {json.dumps({'done': True, 'model': 'glm'})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e), 'model': 'glm'})}\n\n"
                    yield f"data: {json.dumps({'done': True, 'model': 'glm'})}\n\n"
            return StreamingResponse(
                content_generator(),
                media_type="text/event-stream"
            )
        else:
            response = await client.chat.completions.create(
                model=get_model("glm"),
                messages=messages,
                timeout=DEFAULT_TIMEOUT
            )
            return response.choices[0].message.content
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Request to GLM API timed out. Please try again later."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"GLM API error: {str(e)}"
        )

async def call_doubao(messages: List[Dict[str, str]], api_key: str = None, stream: bool = False, language: str = "en"):
    """
    Call the Doubao API for chat completions, using OpenAI-compatible AsyncOpenAI client, just like call_openai.
    """
    key_to_use = api_key or DOUBAO_API_KEY
    if not key_to_use:
        raise HTTPException(status_code=500, detail="Doubao API key not configured")

    # Get the system prompt for Doubao in the specified language
    system_prompt = get_model_prompt("doubao", language) if 'get_model_prompt' in globals() else None
    if system_prompt and not any(msg.get("role") == "system" for msg in messages):
        messages = [
            {"role": "system", "content": system_prompt}
        ] + messages

    try:
        client = AsyncOpenAI(
            api_key=key_to_use,
            base_url=DOUBAO_API_URL,
            max_retries=MAX_RETRIES_COUNT,
        )
        if stream:
            from fastapi.responses import StreamingResponse
            async def content_generator():
                try:
                    stream_response = await client.chat.completions.create(
                        model=get_model("doubao"),
                        messages=messages,
                        stream=True,
                        timeout=DEFAULT_TIMEOUT
                    )
                    async for chunk in stream_response:
                        if chunk.choices and chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            yield f"data: {json.dumps({'content': content, 'model': 'doubao'})}\n\n"
                    yield f"data: {json.dumps({'done': True, 'model': 'doubao'})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e), 'model': 'doubao'})}\n\n"
                    yield f"data: {json.dumps({'done': True, 'model': 'doubao'})}\n\n"
            return StreamingResponse(
                content_generator(),
                media_type="text/event-stream"
            )
        else:
            response = await client.chat.completions.create(
                model=get_model("doubao"),
                messages=messages,
                timeout=DEFAULT_TIMEOUT
            )
            return response.choices[0].message.content
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Request to Doubao API timed out. Please try again later."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Doubao API error: {str(e)}"
        )

async def generate_summary(responses: Dict[str, str], question: str, api_key: str = None, language: str = "en", stream: bool = False):
    """Generate a summary of responses from multiple models.
    
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
    # Use user-provided key if available, otherwise use environment variable
    key_to_use = api_key or DEEPSEEK_API_KEY
    
    # Get the summary prompt for the specified language
    prompt = get_summary_prompt(question, responses, language)
    
    messages = [{"role": "user", "content": prompt}]
    
    # Track errors for better diagnostics
    errors = []
    
    # Try DeepSeek first (if API key is available)
    if key_to_use:
        try:
            return await call_deepseek(messages, key_to_use, stream=stream)
        except HTTPException as e:
            errors.append({"model": "deepseek", "error": str(e.detail), "status": e.status_code})
            print(f"DeepSeek API error: {e.detail}")
        except Exception as e:
            errors.append({"model": "deepseek", "error": str(e), "status": 500})
            print(f"Unexpected error with DeepSeek API: {str(e)}")
    else:
        errors.append({"model": "deepseek", "error": "API key not configured", "status": 500})
    
    # Try OpenAI as first fallback
    if OPENAI_API_KEY:
        try:
            return await call_openai(messages, OPENAI_API_KEY, stream=stream)
        except HTTPException as e:
            errors.append({"model": "openai", "error": str(e.detail), "status": e.status_code})
            print(f"OpenAI API error: {e.detail}")
        except Exception as e:
            errors.append({"model": "openai", "error": str(e), "status": 500})
            print(f"Unexpected error with OpenAI API: {str(e)}")
    else:
        errors.append({"model": "openai", "error": "API key not configured", "status": 500})
    
    # Try Qwen as second fallback
    if QWEN_API_KEY:
        try:
            return await call_qwen(messages, QWEN_API_KEY)
        except HTTPException as e:
            errors.append({"model": "qwen", "error": str(e.detail), "status": e.status_code})
            print(f"Qwen API error: {e.detail}")
        except Exception as e:
            errors.append({"model": "qwen", "error": str(e), "status": 500})
            print(f"Unexpected error with Qwen API: {str(e)}")
    
    # If all attempts failed, raise a detailed error
    error_message = "Failed to generate summary with any available model."
    error_details = json.dumps(errors, indent=2)
    print(f"{error_message} Errors: {error_details}")
    
    raise HTTPException(
        status_code=500,
        detail={
            "message": error_message,
            "errors": errors
        }
    )

# Helper function to decode API key from header
def decode_api_key(req: Request, header_name: str) -> Optional[str]:
    from urllib.parse import unquote
    api_key = req.headers.get(header_name)
    if api_key:
        return unquote(api_key)
    return None

# Individual model API endpoints
@app.post("/api/chat/openai")
async def chat_openai(request: ChatRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        user_openai_key = decode_api_key(req, "X-OpenAI-API-Key")
        return await call_openai(messages, user_openai_key, stream=request.stream, language=request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/grok")
async def chat_grok(request: ChatRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        user_grok_key = decode_api_key(req, "X-Grok-API-Key")
        return await call_grok(messages, user_grok_key, stream=request.stream, language=request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/qwen")
async def chat_qwen(request: ChatRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        user_qwen_key = decode_api_key(req, "X-Qwen-API-Key")
        return await call_qwen(messages, user_qwen_key, stream=request.stream, language=request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/deepseek")
async def chat_deepseek(request: ChatRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        user_deepseek_key = decode_api_key(req, "X-DeepSeek-API-Key")
        return await call_deepseek(messages, user_deepseek_key, stream=request.stream, language=request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/doubao")
async def chat_doubao(request: ChatRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        user_doubao_key = decode_api_key(req, "X-Doubao-API-Key")
        return await call_doubao(messages, user_doubao_key, stream=request.stream, language=request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/glm")
async def chat_glm(request: ChatRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        user_glm_key = decode_api_key(req, "X-GLM-API-Key")
        return await call_glm(messages, user_glm_key, stream=request.stream, language=request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# The combined /api/chat endpoint has been removed in favor of individual model endpoints

@app.post("/api/summary")
async def summary(request: SummaryRequest):
    try:
        # If streaming is requested, return a streaming response
        if request.stream:
            from fastapi.responses import StreamingResponse
            
            # Create a streaming response with the summary content
            async def summary_generator():
                try:
                    # Get the streaming response from generate_summary
                    stream_response = await generate_summary(
                        request.responses, 
                        request.question, 
                        language=request.language,
                        stream=True
                    )
                    
                    # If we got a StreamingResponse, return its content
                    if isinstance(stream_response, StreamingResponse):
                        async for chunk in stream_response.body_iterator:
                            yield chunk
                    else:
                        # If we got a string, wrap it in a JSON response
                        yield f"data: {json.dumps({'content': stream_response, 'model': 'summary'})}\n\n"
                        yield f"data: {json.dumps({'done': True, 'model': 'summary'})}\n\n"
                except Exception as e:
                    # Handle errors during streaming
                    yield f"data: {json.dumps({'error': str(e), 'model': 'summary'})}\n\n"
                    yield f"data: {json.dumps({'done': True, 'model': 'summary'})}\n\n"
            
            return StreamingResponse(
                summary_generator(),
                media_type="text/event-stream"
            )
        else:
            # For non-streaming requests, return a regular JSON response
            summary = await generate_summary(
                request.responses, 
                request.question, 
                language=request.language,
                stream=False
            )
            return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {
        "status": "ok",
        "environment": get_current_env(),
        "log_level": get_log_level(),
        "timestamp": time.time()
    }

@app.get("/api/logs/level")
async def get_current_log_level():
    """Get the current log level"""
    logger.info("Log level endpoint called")
    return {"log_level": get_log_level()}

@app.post("/api/logs/level/{level}")
async def set_log_level(level: str):
    """Set the log level"""
    valid_levels = ["debug", "info", "warning", "error", "critical"]
    
    if level.lower() not in valid_levels:
        logger.warning(f"Invalid log level requested: {level}")
        raise HTTPException(status_code=400, detail=f"Invalid log level. Must be one of: {', '.join(valid_levels)}")
    
    # Set the environment variable
    os.environ["LOG_LEVEL"] = level.lower()
    
    # Update the logger
    logger.setLevel(level.upper())
    logger.info(f"Log level changed to {level}")
    
    return {"log_level": level.lower(), "status": "updated"}

# Configuration endpoints
@app.post("/api/reload-config")
async def reload_config():
    """Reload configuration from environment variables"""
    try:
        # Reload environment variables (if using dotenv)
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        # Update global variables with new values from environment
        global OPENAI_API_KEY, GROK_API_KEY, QWEN_API_KEY, DEEPSEEK_API_KEY
        global OPENAI_API_URL, GROK_API_URL, QWEN_API_URL, DEEPSEEK_API_URL
        
        OPENAI_API_KEY = get_api_key("openai")
        GROK_API_KEY = get_api_key("grok")
        QWEN_API_KEY = get_api_key("qwen")
        DEEPSEEK_API_KEY = get_api_key("deepseek")
        
        OPENAI_API_URL = get_api_url("openai")
        GROK_API_URL = get_api_url("grok")
        QWEN_API_URL = get_api_url("qwen")
        DEEPSEEK_API_URL = get_api_url("deepseek")
        
        return {
            "status": "success", 
            "message": f"Configuration reloaded successfully from environment variables for environment: {get_current_env()}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload configuration: {str(e)}")

@app.post("/api/switch-environment/{env}")
async def change_environment(env: str):
    try:
        if env not in [ENV_DEV, ENV_TEST, ENV_PRD]:
            raise HTTPException(status_code=400, detail=f"Invalid environment: {env}. Must be one of: {ENV_DEV}, {ENV_TEST}, {ENV_PRD}")
        
        switch_environment(env)
        return {
            "status": "success", 
            "message": f"Switched to {env} environment and reloaded configuration",
            "environment": env
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to switch environment: {str(e)}")

@app.get("/api/current-environment")
async def get_environment():
    return {
        "environment": get_current_env(),
        "server_config": {
            "host": get_server_config("host"),
            "port": get_server_config("port"),
            "debug": get_server_config("debug"),
            "log_level": get_server_config("log_level")
        }
    }

if __name__ == "__main__":
    # Get environment from command line if provided
    import sys
    if len(sys.argv) > 1 and sys.argv[1] in [ENV_DEV, ENV_TEST, ENV_PRD]:
        env = sys.argv[1]
        switch_environment(env)
    else:
        env = get_current_env()
    
    # Get server configuration
    host = get_server_config("host")
    port = get_server_config("port")
    debug = get_server_config("debug")
    
    # Ensure configuration is loaded
    print(f"Starting server in {env.upper()} environment with configuration:")
    print(f"OpenAI API Key: {'Configured' if OPENAI_API_KEY else 'Not configured'}")
    print(f"Grok API Key: {'Configured' if GROK_API_KEY else 'Not configured'}")
    print(f"Qwen API Key: {'Configured' if QWEN_API_KEY else 'Not configured'}")
    print(f"DeepSeek API Key: {'Configured' if DEEPSEEK_API_KEY else 'Not configured'}")
    print(f"GLM API Key: {'Configured' if GLM_API_KEY else 'Not configured'}")
    print(f"Server: {host}:{port} (debug: {debug})")
    
    import uvicorn
    uvicorn.run("main:app", host=host, port=port, reload=debug)
