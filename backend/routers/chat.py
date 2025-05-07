import os
import sys
from typing import Any, Dict, List, Optional

import sentry_sdk
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Add the parent directory to path to support both running methods
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Try relative imports first, then fall back to absolute imports
try:
    # For running from backend directory
    from ..env_config import get_api_key
    from ..models import ChatRequest, Message, SummaryRequest
    from ..utils.logger import logger
    from ..utils.model_helpers import (call_deepseek, call_doubao, call_glm,
                                       call_grok, call_openai, call_qwen,
                                       decode_api_key, generate_summary)
    from ..utils.model_prompts import get_model_prompt
    from ..utils.sentry_helpers import track_errors, capture_exception
    from ..utils.language_utils import detect_language
except (ImportError, ValueError):
    # For running from project root with module prefix
    from backend.env_config import get_api_key
    from backend.models import ChatRequest, Message, SummaryRequest
    from backend.utils.logger import logger
    from backend.utils.model_helpers import (call_deepseek, call_doubao,
                                             call_glm, call_grok, call_openai,
                                             call_qwen, decode_api_key,
                                             generate_summary)
    from backend.utils.model_prompts import get_model_prompt
    from backend.utils.sentry_helpers import track_errors, capture_exception
    from backend.utils.language_utils import detect_language

# Create the router
chat_router = APIRouter(prefix="/api/chat")

# Helper function to detect language from messages
def detect_language_from_messages(messages, default_language="en"):
    """
    Detect language from a list of messages, prioritizing the most recent user message.
    
    Args:
        messages: List of message objects with role and content
        default_language: Default language to return if no user messages found
        
    Returns:
        Detected language code ('zh' or 'en')
    """
    # Find the most recent user message
    user_messages = [msg.get("content") if isinstance(msg, dict) else msg.content 
                    for msg in messages 
                    if (isinstance(msg, dict) and msg.get("role") == "user") or 
                       (hasattr(msg, "role") and msg.role == "user")]
    
    if user_messages:
        # Detect language from the last user message
        detected_lang = detect_language(user_messages[-1])
        if detected_lang != default_language:
            logger.info(f"Language auto-detected as {detected_lang}")
        return detected_lang
    
    return default_language

# Summary generation endpoint
@chat_router.post("/summary")
@track_errors
async def generate_model_summary(request: SummaryRequest):
    """
    Generate a summary comparing responses from different models.
    
    Args:
        request: SummaryRequest containing model responses and original question
        
    Returns:
        Streaming or non-streaming summary response
    """
    try:
        # Set Sentry tags for better error tracking
        sentry_sdk.set_tag("feature", "summary")
        sentry_sdk.set_tag("language", request.language)
        if request.stream:
            # For streaming, we need to create an async generator function
            async def summary_stream_generator():
                # Get the model summary generator
                summary_response = await generate_summary(
                    request.responses,
                    request.question,
                    language=request.language,
                    use_streaming=True
                )
                
                # If it's a StreamingResponse, extract the body_iterator
                if hasattr(summary_response, 'body_iterator'):
                    async for chunk in summary_response.body_iterator:
                        yield chunk
                else:
                    # If it's not a StreamingResponse, yield the content as a single chunk
                    yield f"data: {json.dumps({'content': str(summary_response), 'model': 'summary', 'done': True})}\n\n"
            
            # Return the StreamingResponse with our generator
            return StreamingResponse(summary_stream_generator(), media_type="text/event-stream")
        else:
            # For non-streaming, wait for the full response
            result = await generate_summary(
                request.responses,
                request.question,
                language=request.language,
                use_streaming=False
            )
            return result
    except Exception as e:
        # Capture exception with additional context
        extra_context = {
            "language": request.language,
            "streaming": request.stream,
            "model_count": len(request.responses),
            "question_length": len(request.question)
        }
        capture_exception(e, extra_context)
        logger.error(f"Summary generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Summary generation error: {str(e)}")

# Individual model API endpoints
@chat_router.post("/openai")
@track_errors
async def chat_openai(request: ChatRequest, req: Request):
    try:
        # Set Sentry tags for better error tracking
        sentry_sdk.set_tag("model", "openai")
        sentry_sdk.set_tag("mode", "chat")
        
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Auto-detect language if not explicitly set to non-English
        language = request.language
        if language == "en":
            language = detect_language_from_messages(messages, default_language="en")
            
        user_openai_key = decode_api_key(req, "X-OpenAI-API-Key")
        return await call_openai(messages, user_openai_key, use_streaming=request.stream, language=language)
    except Exception as e:
        # Capture exception with additional context
        extra_context = {
            "language": request.language,
            "streaming": request.stream,
            "message_count": len(request.messages)
        }
        capture_exception(e, extra_context)
        logger.error(f"OpenAI chat API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.post("/grok")
async def chat_grok(request: ChatRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Auto-detect language if not explicitly set to non-English
        language = request.language
        if language == "en":
            language = detect_language_from_messages(messages, default_language="en")
            
        user_grok_key = decode_api_key(req, "X-Grok-API-Key")
        return await call_grok(messages, user_grok_key, use_streaming=request.stream, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.post("/qwen")
async def chat_qwen(request: ChatRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Auto-detect language if not explicitly set to non-English
        language = request.language
        if language == "en":
            language = detect_language_from_messages(messages, default_language="en")
            
        user_qwen_key = decode_api_key(req, "X-Qwen-API-Key")
        return await call_qwen(messages, user_qwen_key, use_streaming=request.stream, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.post("/deepseek")
async def chat_deepseek(request: ChatRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Auto-detect language if not explicitly set to non-English
        language = request.language
        if language == "en":
            language = detect_language_from_messages(messages, default_language="en")
            
        user_deepseek_key = decode_api_key(req, "X-DeepSeek-API-Key")
        return await call_deepseek(messages, user_deepseek_key, use_streaming=request.stream, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.post("/doubao")
async def chat_doubao(request: ChatRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Auto-detect language if not explicitly set to non-English
        language = request.language
        if language == "en":
            language = detect_language_from_messages(messages, default_language="en")
            
        user_doubao_key = decode_api_key(req, "X-Doubao-API-Key")
        return await call_doubao(messages, user_doubao_key, use_streaming=request.stream, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.post("/glm")
async def chat_glm(request: ChatRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Auto-detect language if not explicitly set to non-English
        language = request.language
        if language == "en":
            language = detect_language_from_messages(messages, default_language="en")
            
        user_glm_key = decode_api_key(req, "X-GLM-API-Key")
        return await call_glm(messages, user_glm_key, use_streaming=request.stream, language=language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
