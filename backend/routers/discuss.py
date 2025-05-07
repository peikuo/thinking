import json
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
    from ..models import Message
    from ..utils.logger import logger
    from ..utils.model_helpers import (call_deepseek, call_doubao, call_glm,
                                       call_grok, call_openai, call_qwen,
                                       decode_api_key)
    from ..utils.model_prompts import get_model_prompt, DISCUSS_PROMPTS
    from ..utils.sentry_helpers import track_errors, capture_exception
except (ImportError, ValueError):
    # For running from project root with module prefix
    from backend.env_config import get_api_key
    from backend.models import Message
    from backend.utils.logger import logger
    from backend.utils.model_helpers import (call_deepseek, call_doubao,
                                             call_glm, call_grok, call_openai,
                                             call_qwen, decode_api_key)
    from backend.utils.model_prompts import get_model_prompt, DISCUSS_PROMPTS
    from backend.utils.sentry_helpers import track_errors, capture_exception

# Create a request model for discussion mode
class DiscussRequest(BaseModel):
    messages: List[Message]
    previous_response: Optional[str] = None  # The response from the previous model
    previous_model: Optional[str] = None     # Which model gave the previous response
    language: Optional[str] = "en"
    stream: Optional[bool] = True

# Create the router
discuss_router = APIRouter(prefix="/api/discuss")

# Helper function to detect language
def detect_language(text: str) -> str:
    """
    Detect if text is primarily Chinese or English.
    Returns 'zh' for Chinese, 'en' for English or other languages.
    """
    # Simple detection: if more than 10% of characters are Chinese, consider it Chinese
    chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    if chinese_chars / max(len(text), 1) > 0.1:
        return "zh"
    return "en"

# Helper function to format messages for discussion mode
def format_discuss_messages(messages, model_name, previous_model=None, previous_response=None, language="en"):
    """
    Format messages for discussion mode by adding system instructions
    and previous model responses for sequential answering.
    
    This function now handles the full conversation history, ensuring models
    have context from previous exchanges.
    
    If language is not explicitly provided, it will be detected from the user's messages.
    """
    # Auto-detect language from user messages if not explicitly provided
    if language == "en":  # Only try to detect if not explicitly set to non-English
        # Find the most recent user message
        user_messages = [msg.get("content") if isinstance(msg, dict) else msg.content 
                        for msg in messages 
                        if (isinstance(msg, dict) and msg.get("role") == "user") or 
                           (hasattr(msg, "role") and msg.role == "user")]
        
        if user_messages:
            # Detect language from the last user message
            detected_lang = detect_language(user_messages[-1])
            if detected_lang != language:
                logger.info(f"Language auto-detected as {detected_lang} for model {model_name}")
                language = detected_lang
    
    # Get base system message template
    system_content = DISCUSS_PROMPTS["base"][language].format(model_name=model_name)
    
    # If there's a previous response, ask this model to analyze it
    if previous_response and previous_model:
        # Add the analyze_previous template
        analyze_template = DISCUSS_PROMPTS["analyze_previous"][language]
        system_content += analyze_template.format(
            previous_model=previous_model,
            previous_response=previous_response
        )
    else:
        # First model doesn't need to analyze previous responses but should still be comprehensive
        system_content += DISCUSS_PROMPTS["first_model"][language]
    
    # Add instructions about conversation history
    if len(messages) > 1:  # If there's conversation history
        if language == "zh":
            system_content += "\n\n请注意，消息历史记录包含了之前的对话。请考虑这些历史记录，以便提供连贯的回应。"
        else:
            system_content += "\n\nPlease note that the message history contains previous exchanges. Consider this history to provide a coherent response."
    
    system_message = {"role": "system", "content": system_content}
    
    # Process messages to ensure proper formatting
    processed_messages = []
    for msg in messages:
        # Ensure we have a proper message format
        processed_msg = {
            "role": msg.get("role") if isinstance(msg, dict) else msg.role,
            "content": msg.get("content") if isinstance(msg, dict) else msg.content
        }
        processed_messages.append(processed_msg)
    
    # Insert system message at the beginning
    formatted_messages = [system_message] + processed_messages
    
    return formatted_messages

# Request model for summary generation
class SummaryRequest(BaseModel):
    user_prompt: str
    responses: Dict[str, str]
    language: Optional[str] = "en"
    stream: Optional[bool] = True

# Helper function to format messages for summary generation
def format_summary_messages(user_prompt, responses, language="en"):
    """
    Format messages for summary generation by combining all discussion content
    and adding system instructions for summarization.
    """
    # Combine all responses into a single text
    all_responses = ""
    for model, response in responses.items():
        all_responses += f"\n\n{model.upper()} RESPONSE:\n{response}"
    
    # Create system message with instructions
    if language == "zh":
        system_content = """你是一位专业的总结专家。请对以下讨论进行全面而自然的总结，提炼出关键见解和最佳解决方案。

你的总结应该涵盖以下内容，但请以自然流畅的方式写作，不要使用编号或明显的段落标记：

- 明确讨论的核心问题和主要关注点
- 整合所有观点中的关键见解，不提及具体模型名称
- 指出各个观点之间的共识和分歧
- 基于所有讨论，提出全面、平衡的解决方案
- 简明扼要地总结主要发现和结论

请以自然、流畅的方式写作，就像你在与读者进行对话。你的总结应该客观、全面，避免偏向任何单一观点，并且不要提及是哪个模型提出了哪个观点。专注于内容本身，而不是内容的来源。"""
    else:
        system_content = """You are a professional summarization expert. Please provide a natural, flowing summary of the following discussion, extracting key insights and the best solution approach.

Your summary should cover these elements, but please write in a natural, conversational style without using numbered sections or explicit paragraph markers:

- Clarify the central issue and main focus of the discussion
- Integrate key points from all responses without mentioning specific model names
- Identify common ground and divergent viewpoints across the responses
- Offer a comprehensive, balanced solution based on all perspectives shared
- Concisely present the main findings and conclusions

Write as if you're having a conversation with the reader. Your summary should be objective and comprehensive, avoiding bias toward any single viewpoint, and should not mention which model proposed which idea. Focus on the content itself, not the source of the content."""
    
    # Create user message with the discussion content
    if language == "zh":
        user_content = f"用户问题: {user_prompt}\n\n各方回应:{all_responses}"
    else:
        user_content = f"User question: {user_prompt}\n\nResponses:{all_responses}"
    
    # Format messages
    system_message = {"role": "system", "content": system_content}
    user_message = {"role": "user", "content": user_content}
    
    return [system_message, user_message]

# Individual model API endpoints for discussion mode
@discuss_router.post("/openai")
@track_errors
async def discuss_openai(request: DiscussRequest, req: Request):
    try:
        # Set Sentry transaction name for better tracking
        sentry_sdk.set_tag("model", "openai")
        sentry_sdk.set_tag("mode", "discuss")
        
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        formatted_messages = format_discuss_messages(
            messages, 
            model_name="OpenAI",
            previous_model=request.previous_model,
            previous_response=request.previous_response,
            language=request.language
        )
        user_openai_key = decode_api_key(req, "X-OpenAI-API-Key")
        return await call_openai(formatted_messages, user_openai_key, use_streaming=request.stream, language=request.language)
    except Exception as e:
        # Capture exception with additional context
        extra_context = {
            "language": request.language,
            "streaming": request.stream,
            "message_count": len(request.messages),
            "has_previous_response": request.previous_response is not None
        }
        capture_exception(e, extra_context)
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
        return await call_grok(formatted_messages, user_grok_key, use_streaming=request.stream, language=request.language)
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
        return await call_qwen(formatted_messages, user_qwen_key, use_streaming=request.stream, language=request.language)
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
        return await call_deepseek(formatted_messages, user_deepseek_key, use_streaming=request.stream, language=request.language)
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
        return await call_doubao(formatted_messages, user_doubao_key, use_streaming=request.stream, language=request.language)
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
        return await call_glm(formatted_messages, user_glm_key, use_streaming=request.stream, language=request.language)
    except Exception as e:
        logger.error(f"GLM discuss API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Summary generation endpoint
@discuss_router.post("/summary")
async def generate_discussion_summary(request: SummaryRequest, req: Request):
    try:
        # Format messages for summary generation
        formatted_messages = format_summary_messages(
            request.user_prompt,
            request.responses,
            language=request.language
        )
        
        # Choose model based on language
        if request.language == "zh":
            # For Chinese, use deepseek first, fall back to qwen
            try:
                user_deepseek_key = decode_api_key(req, "X-DeepSeek-API-Key")
                return await call_deepseek(formatted_messages, user_deepseek_key, use_streaming=request.stream, language=request.language)
            except Exception as deepseek_error:
                logger.warning(f"DeepSeek summary error, falling back to Qwen: {str(deepseek_error)}")
                user_qwen_key = decode_api_key(req, "X-Qwen-API-Key")
                return await call_qwen(formatted_messages, user_qwen_key, use_streaming=request.stream, language=request.language)
        else:
            # For English, use qwen first, fall back to deepseek
            try:
                user_qwen_key = decode_api_key(req, "X-Qwen-API-Key")
                return await call_qwen(formatted_messages, user_qwen_key, use_streaming=request.stream, language=request.language)
            except Exception as qwen_error:
                logger.warning(f"Qwen summary error, falling back to DeepSeek: {str(qwen_error)}")
                user_deepseek_key = decode_api_key(req, "X-DeepSeek-API-Key")
                return await call_deepseek(formatted_messages, user_deepseek_key, use_streaming=request.stream, language=request.language)
    except Exception as e:
        logger.error(f"Summary generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
