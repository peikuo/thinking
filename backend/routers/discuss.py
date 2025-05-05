import json
import os
import sys
from typing import Any, Dict, List, Optional

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
    from ..utils.model_prompts import get_model_prompt
except (ImportError, ValueError):
    # For running from project root with module prefix
    from backend.env_config import get_api_key
    from backend.models import Message
    from backend.utils.logger import logger
    from backend.utils.model_helpers import (call_deepseek, call_doubao,
                                             call_glm, call_grok, call_openai,
                                             call_qwen, decode_api_key)
    from backend.utils.model_prompts import get_model_prompt

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
        system_content = f"你是 {model_name} 模型。你是一位深思熟虑、善于分析的专家。"
    else:
        system_content = f"You are the {model_name} model. You are a thoughtful, analytical expert."
    
    # If there's a previous response, ask this model to analyze it
    if previous_response and previous_model:
        if language == "zh":
            system_content += f"\n\n{previous_model} 模型已经回答了这个问题。他们的回答是:\n\n\"\"\"{previous_response}\"\"\"\n\n"
            system_content += "请遵循以下步骤进行回应：\n\n"
            system_content += "1. **分析前一个回答**：首先，仔细分析上面的回答，指出其中的优点、不足和可能存在的盲点。评估其逻辑性、全面性和准确性。\n"
            system_content += "2. **提供你的视角**：结合前一个回答中的有价值观点，提供你自己独特的见解。特别关注前一个回答中未充分探讨的方面。\n"
            system_content += "3. **深入探讨**：对问题进行更深层次的分析，考虑不同角度、潜在影响和长期后果。\n"
            system_content += "4. **给出我的方案**：如果适用，提供具体、可操作的建议或解决方案。\n"
            system_content += "5. **总结关键点**：最后，总结你的主要观点和见解，强调与前一个回答的不同之处。\n\n"
            system_content += "你的回答应该全面、深入、有洞察力，并且能够展示你独特的思考方式。避免简单重复前一个回答的内容。"
        else:
            system_content += f"\n\n{previous_model} has already answered this question. Their response was:\n\n\"\"\"{previous_response}\"\"\"\n\n"
            system_content += "Please follow these steps in your response:\n\n"
            system_content += "1. **Analyze the previous response**: First, carefully analyze the above response, identifying its strengths, limitations, and potential blind spots. Evaluate its logical coherence, comprehensiveness, and accuracy.\n"
            system_content += "2. **Provide your perspective**: Incorporate valuable insights from the previous response while offering your unique viewpoint. Pay special attention to aspects that weren't fully explored in the previous answer.\n"
            system_content += "3. **Deepen the analysis**: Examine the question at a deeper level, considering different angles, potential implications, and long-term consequences.\n"
            system_content += "4. **Present my solution**: If applicable, provide specific, actionable advice or solutions.\n"
            system_content += "5. **Summarize key points**: Finally, summarize your main points and insights, highlighting how they differ from the previous response.\n\n"
            system_content += "Your answer should be comprehensive, insightful, and demonstrate your unique thinking process. Avoid simply repeating content from the previous response."
    else:
        # First model doesn't need to analyze previous responses but should still be comprehensive
        if language == "zh":
            system_content += "\n\n请遵循以下步骤回答用户的问题：\n\n"
            system_content += "1. **全面理解问题**：首先确保你完全理解了问题的各个方面和潜在的复杂性。\n"
            system_content += "2. **提供深入分析**：对问题进行多角度、多层次的分析，考虑不同的观点和可能的影响。\n"
            system_content += "3. **引用相关知识**：适当引用相关领域的知识、理论或最佳实践来支持你的观点。\n"
            system_content += "4. **给出我的方案**：如果适用，提供明确、可操作的建议或解决方案。\n"
            system_content += "5. **总结关键见解**：最后，总结你的主要观点和见解。\n\n"
            system_content += "你的回答应该全面、深入、有洞察力，并且能够展示你作为专业模型的思考能力。"
        else:
            system_content += "\n\nPlease follow these steps to answer the user's question:\n\n"
            system_content += "1. **Understand the question fully**: First ensure you comprehend all aspects of the question and its potential complexities.\n"
            system_content += "2. **Provide in-depth analysis**: Analyze the question from multiple perspectives and levels, considering different viewpoints and possible implications.\n"
            system_content += "3. **Reference relevant knowledge**: Where appropriate, reference relevant domain knowledge, theories, or best practices to support your points.\n"
            system_content += "4. **Present my solution**: If applicable, provide clear, actionable advice or solutions.\n"
            system_content += "5. **Summarize key insights**: Finally, summarize your main points and insights.\n\n"
            system_content += "Your response should be comprehensive, thoughtful, and demonstrate your capabilities as a sophisticated model."
    
    system_message = {"role": "system", "content": system_content}
    
    # Insert system message at the beginning
    formatted_messages = [system_message] + messages
    
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
        return await call_openai(formatted_messages, user_openai_key, use_streaming=request.stream, language=request.language)
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
