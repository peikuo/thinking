from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import httpx
import os
import asyncio
import json
from openai import AsyncOpenAI

# Import environment-based configuration module
from env_config import (
    get_api_key, get_api_url, get_model, get_server_config,
    get_current_env, switch_environment, 
    ENV_DEV, ENV_TEST, ENV_PRD
)

app = FastAPI(title="Thinking API", description="API for the Thinking project")

# CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, in production specify the actual origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get API keys and URLs from configuration
OPENAI_API_KEY = get_api_key("openai")
GROK_API_KEY = get_api_key("grok")
QWEN_API_KEY = get_api_key("qwen")
DEEPSEEK_API_KEY = get_api_key("deepseek")

# API endpoints
OPENAI_API_URL = get_api_url("openai")
GROK_API_URL = get_api_url("grok")
QWEN_API_URL = get_api_url("qwen")
DEEPSEEK_API_URL = get_api_url("deepseek")

# Default timeout for API calls (in seconds)
DEFAULT_TIMEOUT = 60.0

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
async def call_openai(messages: List[Dict[str, str]], api_key: str = None, stream: bool = False):
    # Use user-provided key if available, otherwise use environment variable
    key_to_use = api_key or OPENAI_API_KEY
    
    if not key_to_use:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    print("openai trace: ", messages)
    try:
        # Create an OpenAI client with the API key
        client = AsyncOpenAI(
            api_key=key_to_use,
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

async def call_grok(messages: List[Dict[str, str]], api_key: str = None, stream: bool = False):
    # Use user-provided key if available, otherwise use environment variable
    key_to_use = api_key or GROK_API_KEY
    print("grok trace: ", messages)
    if not key_to_use:
        raise HTTPException(status_code=500, detail="Grok API key not configured")
    
    # Add system prompt for Grok
    grok_messages = [
        {
            "role": "system",
            "content": "你是由xAI创建的Grok 3，一个专为问答设计的AI助手。你的目标是提供清晰、准确且有帮助的回答，以满足用户的问题或需求。以下是你的指导原则：\n\n以简洁、自然的语言回答问题，除非用户要求详细解释。\n如果问题含糊不清，礼貌地请求澄清，并提供可能的解释方向。\n根据需要利用你的知识和分析能力，确保回答基于事实和逻辑。\n如果问题涉及特定数据（如X用户资料、帖子、链接或上传内容），仅在用户明确要求时使用你的附加工具进行分析。\n如果需要更多信息，可以搜索网络或X上的帖子，但优先使用你的现有知识。\n如果用户似乎想要生成图像，询问确认，而不是直接生成。\n对于敏感问题（如涉及死亡或惩罚），说明你作为AI无法做出此类判断。\n当前日期是2025年4月3日，仅在用户询问时提及。\n保持中立，避免主观判断或偏见，尤其是关于在线信息真伪的评价。\n以友好、专业的语气与用户互动，始终以提供最大价值为目标。"
        }
    ] + messages
    
    try:
        # Create an OpenAI client with the API key and X.AI base URL
        client = AsyncOpenAI(
            api_key=key_to_use,
            base_url=GROK_API_URL
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

async def call_qwen(messages: List[Dict[str, str]], api_key: str = None, stream: bool = False):
    # Use user-provided key if available, otherwise use environment variable
    key_to_use = api_key or QWEN_API_KEY
    
    if not key_to_use:
        raise HTTPException(status_code=500, detail="Qwen API key not configured")
    
    # Convert messages to Qwen format
    prompt = ""
    for message in messages:
        if message["role"] == "user":
            prompt += f"Human: {message['content']}\n"
        elif message["role"] == "assistant":
            prompt += f"Assistant: {message['content']}\n"
    
    prompt += "Assistant: "
    
    try:
        # Create an OpenAI client with the API key and Qwen base URL
        client = AsyncOpenAI(
            api_key=key_to_use,
            base_url=QWEN_API_URL
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

async def call_deepseek(messages: List[Dict[str, str]], api_key: str = None, stream: bool = False):
    # Use user-provided key if available, otherwise use environment variable
    key_to_use = api_key or DEEPSEEK_API_KEY
    
    if not key_to_use:
        raise HTTPException(status_code=500, detail="DeepSeek API key not configured")
    
    try:
        # Create an OpenAI client with the API key and DeepSeek base URL
        client = AsyncOpenAI(
            api_key=key_to_use,
            base_url=DEEPSEEK_API_URL
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
    
    # Create prompts for different languages
    prompts = {
        "en": f"""
        Analyze and summarize the responses from four different AI models to the following question:
        
        Question: {question}
        
        Here are the responses:
        
        OpenAI: {responses.get('openai', 'No response')}
        
        Grok: {responses.get('grok', 'No response')}
        
        Qwen: {responses.get('qwen', 'No response')}
        
        DeepSeek: {responses.get('deepseek', 'No response')}
        
        Provide a factual, objective summary that includes:
        1. Common points shared by multiple models
        2. Differences in their approaches or conclusions
        3. Key information presented across the responses
        4. Areas where models provide complementary information
        5. Any significant disagreements between models
        
        Focus solely on analyzing the content of the responses without adding your own opinions or subjective judgments. Format your response in clear sections with headings.
        """,
        
        "zh": f"""
        分析并总结四个不同AI模型对以下问题的回答：
        
        问题：{question}
        
        以下是各模型的回答：
        
        OpenAI：{responses.get('openai', '无回应')}
        
        Grok：{responses.get('grok', '无回应')}
        
        Qwen：{responses.get('qwen', '无回应')}
        
        DeepSeek：{responses.get('deepseek', '无回应')}
        
        请提供一个客观、事实性的总结，包括：
        1. 多个模型共同提到的观点
        2. 它们在方法或结论上的差异
        3. 各回答中呈现的关键信息
        4. 模型提供互补信息的领域
        5. 模型之间存在的任何重大分歧
        
        请仅关注分析回答的内容，不要添加自己的观点或主观判断。请以清晰的章节和标题格式化您的回答。
        """
    }
    
    # Use the prompt for the specified language, default to English if not available
    prompt = prompts.get(language, prompts["en"])
    
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
        return await call_openai(messages, user_openai_key, stream=request.stream)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/grok")
async def chat_grok(request: ChatRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        user_grok_key = decode_api_key(req, "X-Grok-API-Key")
        return await call_grok(messages, user_grok_key, stream=request.stream)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/qwen")
async def chat_qwen(request: ChatRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        user_qwen_key = decode_api_key(req, "X-Qwen-API-Key")
        return await call_qwen(messages, user_qwen_key, stream=request.stream)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/deepseek")
async def chat_deepseek(request: ChatRequest, req: Request):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        user_deepseek_key = decode_api_key(req, "X-DeepSeek-API-Key")
        return await call_deepseek(messages, user_deepseek_key, stream=request.stream)
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
    return {"status": "ok"}

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
    print(f"Server: {host}:{port} (debug: {debug})")
    
    import uvicorn
    uvicorn.run("main:app", host=host, port=port, reload=debug)
