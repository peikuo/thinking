from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from fastapi.responses import StreamingResponse
import json

import os
import sys

# Add the parent directory to path to support both running methods
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Try relative imports first, then fall back to absolute imports
try:
    # For running from backend directory
    from ..models import Message
    from ..env_config import get_api_key
    from ..utils.logger import logger
    from ..utils.model_prompts import get_model_prompt
    from ..utils.model_helpers import (
        call_openai, call_grok, call_qwen, call_deepseek, 
        call_glm, call_doubao, decode_api_key
    )
except (ImportError, ValueError):
    # For running from project root with module prefix
    from backend.models import Message
    from backend.env_config import get_api_key
    from backend.utils.logger import logger
    from backend.utils.model_prompts import get_model_prompt
    from backend.utils.model_helpers import (
        call_openai, call_grok, call_qwen, call_deepseek, 
        call_glm, call_doubao, decode_api_key
    )

# Create a request model for discussion mode
class DiscussRequest(BaseModel):
    messages: List[Message]
    previous_response: Optional[str] = None  # The response from the previous model
    previous_model: Optional[str] = None     # Which model gave the previous response
    language: Optional[str] = "en"
    stream: Optional[bool] = True

# Create the router
discuss_router = APIRouter(prefix="/api/discuss")

# Helper function to format messages for discussion mode
def format_discuss_messages(messages, model_name, previous_model=None, previous_response=None, language="en"):
    """
    Format messages for discussion mode by adding system instructions
    and previous model responses for sequential answering.
    """
    # Base system message
    if language == "zh":
        system_content = f"你是 {model_name} 模型。请回答用户的问题。"
    else:
        system_content = f"You are the {model_name} model. Please respond to the user's question."
    
    # If there's a previous response, ask this model to analyze it
    if previous_response and previous_model:
        if language == "zh":
            system_content += f"\n\n{previous_model} 模型已经回答了这个问题。他们的回答是:\n\n\"\"\"{previous_response}\"\"\"\n\n"
            system_content += "请先分析上面的回答，指出其中的优点和不足，然后提供你自己的回答，增加新的观点或见解。"
        else:
            system_content += f"\n\n{previous_model} has already answered this question. Their response was:\n\n\"\"\"{previous_response}\"\"\"\n\n"
            system_content += "Please first analyze the above response, noting its strengths and limitations, then provide your own answer with additional perspectives or insights."
    else:
        # First model doesn't need to analyze previous responses
        if language == "zh":
            system_content += "请提供一个全面、深思熟虑的回答。"
        else:
            system_content += "Please provide a comprehensive, thoughtful response."
    
    system_message = {"role": "system", "content": system_content}
    
    # Insert system message at the beginning
    formatted_messages = [system_message] + messages
    
    return formatted_messages

# Individual model API endpoints for discussion mode
@discuss_router.post("/openai")
async def discuss_openai(request: DiscussRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        formatted_messages = format_discuss_messages(
            messages, 
            model_name="OpenAI",
            previous_model=request.previous_model,
            previous_response=request.previous_response,
            language=request.language
        )
        user_openai_key = decode_api_key(req, "X-OpenAI-API-Key")
        return await call_openai(formatted_messages, user_openai_key, stream=request.stream, language=request.language)
    except Exception as e:
        logger.error(f"OpenAI discuss API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@discuss_router.post("/grok")
async def discuss_grok(request: DiscussRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        formatted_messages = format_discuss_messages(
            messages,
            model_name="Grok",
            previous_model=request.previous_model,
            previous_response=request.previous_response,
            language=request.language
        )
        user_grok_key = decode_api_key(req, "X-Grok-API-Key")
        return await call_grok(formatted_messages, user_grok_key, stream=request.stream, language=request.language)
    except Exception as e:
        logger.error(f"Grok discuss API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@discuss_router.post("/qwen")
async def discuss_qwen(request: DiscussRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        formatted_messages = format_discuss_messages(
            messages,
            model_name="Qwen",
            previous_model=request.previous_model,
            previous_response=request.previous_response,
            language=request.language
        )
        user_qwen_key = decode_api_key(req, "X-Qwen-API-Key")
        return await call_qwen(formatted_messages, user_qwen_key, stream=request.stream, language=request.language)
    except Exception as e:
        logger.error(f"Qwen discuss API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@discuss_router.post("/deepseek")
async def discuss_deepseek(request: DiscussRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        formatted_messages = format_discuss_messages(
            messages,
            model_name="DeepSeek",
            previous_model=request.previous_model,
            previous_response=request.previous_response,
            language=request.language
        )
        user_deepseek_key = decode_api_key(req, "X-DeepSeek-API-Key")
        return await call_deepseek(formatted_messages, user_deepseek_key, stream=request.stream, language=request.language)
    except Exception as e:
        logger.error(f"DeepSeek discuss API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@discuss_router.post("/doubao")
async def discuss_doubao(request: DiscussRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        formatted_messages = format_discuss_messages(
            messages,
            model_name="Doubao",
            previous_model=request.previous_model,
            previous_response=request.previous_response,
            language=request.language
        )
        user_doubao_key = decode_api_key(req, "X-Doubao-API-Key")
        return await call_doubao(formatted_messages, user_doubao_key, stream=request.stream, language=request.language)
    except Exception as e:
        logger.error(f"Doubao discuss API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@discuss_router.post("/glm")
async def discuss_glm(request: DiscussRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        formatted_messages = format_discuss_messages(
            messages,
            model_name="GLM",
            previous_model=request.previous_model,
            previous_response=request.previous_response,
            language=request.language
        )
        user_glm_key = decode_api_key(req, "X-GLM-API-Key")
        return await call_glm(formatted_messages, user_glm_key, stream=request.stream, language=request.language)
    except Exception as e:
        logger.error(f"GLM discuss API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
