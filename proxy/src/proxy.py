import json
import logging
# Logging setup
import os
from logging.handlers import RotatingFileHandler
from typing import AsyncGenerator

import httpx
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

MODEL_CONFIGS = {
    "openai": {
        "url": os.getenv("OPENAI_API_URL"),
    },
    "grok": {
        "url": os.getenv("GROK_API_URL"),
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
    openai_client = OpenAI(
        api_key=api_key,
        base_url=MODEL_CONFIGS["openai"]["url"]
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
    def event_stream():
        try:
            logger.info(f"[OPENAI] Streaming ChatCompletion: model={model}")
            response = openai_client.chat.completions.create(**body, stream=True)
            for chunk in response:
                yield json.dumps(chunk).encode("utf-8") + b"\n"
            logger.info("[OPENAI] Streaming completed.")
        except Exception as e:
            logger.error(f"[OPENAI] Error during streaming: {e}")
            yield json.dumps({"error": str(e)}).encode("utf-8")
    return StreamingResponse(event_stream(), media_type="application/json")

@app.api_route("/grok/v1/chat/completions", methods=["POST"])
async def grok_proxy(request: Request):
    logger.info(f"[GROK] Request: path={request.url.path}, headers={{k: v for k, v in request.headers.items() if k.lower() != 'authorization'}}, client={request.client}")
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        logger.warning("[GROK] Missing or invalid Authorization header.")
        return JSONResponse({"error": "Missing or invalid Authorization header."}, status_code=401)
    
    api_key = auth_header.split(" ", 1)[1]
    grok_api_url = MODEL_CONFIGS["grok"]["url"]
    
    if not grok_api_url:
        logger.error("[GROK] API URL not configured.")
        return JSONResponse({"error": "Grok API URL not configured."}, status_code=500)
    
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
    
    def event_stream():
        try:
            logger.info(f"[GROK] Streaming ChatCompletion: model={model}")
            # Use the dedicated Grok client
            response = grok_client.chat.completions.create(**body, stream=True)
            for chunk in response:
                yield json.dumps(chunk).encode("utf-8") + b"\n"
                
            logger.info("[GROK] Streaming completed.")
        except Exception as e:
            logger.error(f"[GROK] Error during streaming: {e}")
            yield json.dumps({"error": str(e)}).encode("utf-8")
    
    return StreamingResponse(event_stream(), media_type="application/json")
