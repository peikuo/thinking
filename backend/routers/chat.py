from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

import os
import sys

# Add the parent directory to path to support both running methods
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Try relative imports first, then fall back to absolute imports
try:
    # For running from backend directory
    from ..models import Message, ChatRequest, SummaryRequest
    from ..env_config import get_api_key
    from ..utils.logger import logger
    from ..utils.model_prompts import get_model_prompt
    from ..utils.model_helpers import (
        call_openai, call_grok, call_qwen, call_deepseek, 
        call_glm, call_doubao, decode_api_key, generate_summary
    )
except (ImportError, ValueError):
    # For running from project root with module prefix
    from backend.models import Message, ChatRequest, SummaryRequest
    from backend.env_config import get_api_key
    from backend.utils.logger import logger
    from backend.utils.model_prompts import get_model_prompt
    from backend.utils.model_helpers import (
        call_openai, call_grok, call_qwen, call_deepseek, 
        call_glm, call_doubao, decode_api_key, generate_summary
    )

# Create the router
chat_router = APIRouter(prefix="/api/chat")

# Summary generation endpoint
@chat_router.post("/summary")
async def generate_model_summary(request: SummaryRequest):
    """
    Generate a summary comparing responses from different models.
    
    Args:
        request: SummaryRequest containing model responses and original question
        
    Returns:
        Streaming or non-streaming summary response
    """
    try:
        if request.stream:
            # For streaming, use StreamingResponse
            return StreamingResponse(
                generate_summary(
                    request.responses,
                    request.question,
                    language=request.language,
                    stream=True
                ),
                media_type="text/event-stream"
            )
        else:
            # For non-streaming, wait for the full response
            result = await generate_summary(
                request.responses,
                request.question,
                language=request.language,
                stream=False
            )
            return result
    except Exception as e:
        logger.error(f"Summary generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Summary generation error: {str(e)}")

# Individual model API endpoints
@chat_router.post("/openai")
async def chat_openai(request: ChatRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        user_openai_key = decode_api_key(req, "X-OpenAI-API-Key")
        return await call_openai(messages, user_openai_key, stream=request.stream, language=request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.post("/grok")
async def chat_grok(request: ChatRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        user_grok_key = decode_api_key(req, "X-Grok-API-Key")
        return await call_grok(messages, user_grok_key, stream=request.stream, language=request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.post("/qwen")
async def chat_qwen(request: ChatRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        user_qwen_key = decode_api_key(req, "X-Qwen-API-Key")
        return await call_qwen(messages, user_qwen_key, stream=request.stream, language=request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.post("/deepseek")
async def chat_deepseek(request: ChatRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        user_deepseek_key = decode_api_key(req, "X-DeepSeek-API-Key")
        return await call_deepseek(messages, user_deepseek_key, stream=request.stream, language=request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.post("/doubao")
async def chat_doubao(request: ChatRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        user_doubao_key = decode_api_key(req, "X-Doubao-API-Key")
        return await call_doubao(messages, user_doubao_key, stream=request.stream, language=request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chat_router.post("/glm")
async def chat_glm(request: ChatRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        user_glm_key = decode_api_key(req, "X-GLM-API-Key")
        return await call_glm(messages, user_glm_key, stream=request.stream, language=request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
