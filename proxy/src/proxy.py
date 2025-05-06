import json
import logging
# Logging setup
import os
from logging.handlers import RotatingFileHandler
import json

import openai
from openai import OpenAI
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(BASE_DIR, "proxy", "proxy.log")
LOG_DIR = os.path.dirname(LOG_PATH)
if LOG_DIR and not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)
logger = logging.getLogger("proxy")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(message)s')
file_handler = RotatingFileHandler(LOG_PATH, maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

app = FastAPI()

# Hard-coded API URLs for OpenAI and Grok
MODEL_CONFIGS = {
    "openai": {
        # Use environment variable if available, otherwise use hard-coded URL
        "url": os.getenv("OPENAI_API_URL", "https://api.openai.com/v1"),
    },
    "grok": {
        # Use environment variable if available, otherwise use hard-coded URL
        "url": os.getenv("GROK_API_URL", "https://api.x.ai/v1"),
    },
}

@app.api_route("/openai/v1/chat/completions", methods=["POST"])
async def openai_proxy(request: Request):
    logger.info(f"[OPENAI] Request: path={request.url.path}, headers={{k: v for k, v in request.headers.items() if k.lower() != 'authorization'}}, client={request.client}")
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        logger.warning("[OPENAI] Missing or invalid Authorization header.")
        return JSONResponse({"error": "Missing or invalid Authorization header."}, status_code=401)
    api_key = auth_header.split(" ", 1)[1]
    
    # Get the API URL, using the hard-coded default if not available
    openai_api_url = MODEL_CONFIGS["openai"]["url"]
    if not openai_api_url:
        logger.warning("[OPENAI] Using default API URL")
        openai_api_url = "https://api.openai.com/v1"
        
    # Create the OpenAI client
    openai_client = OpenAI(
        api_key=api_key,
        base_url=openai_api_url
    )
    try:
        body = await request.json()
    except Exception as e:
        logger.error(f"[OPENAI] Invalid JSON body: {e}")
        return JSONResponse({"error": "Invalid JSON body."}, status_code=400)
    model = body.get("model")
    stream = body.get("stream", False)
    if not model:
        logger.warning("[OPENAI] Missing model parameter.")
        return JSONResponse({"error": "Missing model parameter."}, status_code=400)
    if not stream:
        logger.warning("[OPENAI] Only streaming mode is supported.")
        return JSONResponse({"error": "Only streaming mode is supported."}, status_code=400)
    async def event_stream():
        try:
            logger.info(f"[OPENAI] Streaming ChatCompletion: model={model}")
            # Create a copy of the body to avoid modifying the original
            request_body = body.copy()
            # Ensure stream is set to True (it's already in the body, but we want to be explicit)
            request_body["stream"] = True
            
            # Use the OpenAI client to make the request
            # The create method returns a Stream object when stream=True
            response = openai_client.chat.completions.create(**request_body)
            
            # The Stream object needs to be iterated with for, not async for
            for chunk in response:
                # Pass the raw chunk through as JSON
                # This preserves the structure but ensures it's properly serialized
                chunk_json = chunk.model_dump()
                # The client expects SSE format with 'data: ' prefix
                yield f"data: {json.dumps(chunk_json)}\n\n".encode("utf-8")
            # Send a final done message
            yield f"data: {json.dumps({'content': '', 'model': 'openai', 'done': True})}\n\n".encode("utf-8")
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield f"data: {json.dumps({'content': error_msg, 'model': 'openai', 'error': True})}\n\n".encode("utf-8")
            yield f"data: {json.dumps({'content': '', 'model': 'openai', 'done': True})}\n\n".encode("utf-8")
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.api_route("/grok/v1/chat/completions", methods=["POST"])
async def grok_proxy(request: Request):
    logger.info(f"[GROK] Request: path={request.url.path}, headers={{k: v for k, v in request.headers.items() if k.lower() != 'authorization'}}, client={request.client}")
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        logger.warning("[GROK] Missing or invalid Authorization header.")
        return JSONResponse({"error": "Missing or invalid Authorization header."}, status_code=401)
    
    api_key = auth_header.split(" ", 1)[1]
    
    # Get the API URL, using the hard-coded default if not available
    grok_api_url = MODEL_CONFIGS["grok"]["url"]
    if not grok_api_url:
        logger.warning("[GROK] Using default API URL")
        grok_api_url = "https://api.x.ai/v1"
    
    try:
        body = await request.json()
    except Exception as e:
        logger.error(f"[GROK] Invalid JSON body: {e}")
        return JSONResponse({"error": "Invalid JSON body."}, status_code=400)
    
    model = body.get("model")
    stream = body.get("stream", False)
    
    if not model:
        logger.warning("[GROK] Missing model parameter.")
        return JSONResponse({"error": "Missing model parameter."}, status_code=400)
    
    if not stream:
        logger.warning("[GROK] Only streaming mode is supported.")
        return JSONResponse({"error": "Only streaming mode is supported."}, status_code=400)
    
    # Create a separate OpenAI client instance for Grok API
    grok_client = OpenAI(
        api_key=api_key,
        base_url=grok_api_url
    )
    
    async def event_stream():
        try:
            logger.info(f"[GROK] Streaming ChatCompletion: model={model}")
            # Create a copy of the body to avoid modifying the original
            request_body = body.copy()
            # Ensure stream is set to True (it's already in the body, but we want to be explicit)
            request_body["stream"] = True
            
            # Use the OpenAI client to make the request
            # The create method returns a Stream object when stream=True
            response = grok_client.chat.completions.create(**request_body)
            
            # The Stream object needs to be iterated with for, not async for
            for chunk in response:
                # Pass the raw chunk through as JSON
                # This preserves the structure but ensures it's properly serialized
                chunk_json = chunk.model_dump()
                # The client expects SSE format with 'data: ' prefix
                yield f"data: {json.dumps(chunk_json)}\n\n".encode("utf-8")
            # Send a final done message
            yield f"data: {json.dumps({'content': '', 'model': 'grok', 'done': True})}\n\n".encode("utf-8")
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield f"data: {json.dumps({'content': error_msg, 'model': 'grok', 'error': True})}\n\n".encode("utf-8")
            yield f"data: {json.dumps({'content': '', 'model': 'grok', 'done': True})}\n\n".encode("utf-8")
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")
