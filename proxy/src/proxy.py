import os
import json
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
from typing import AsyncGenerator
import openai
import logging
from logging.handlers import RotatingFileHandler

# Logging setup
LOG_PATH = "proxy/proxy.log"
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
    openai.api_key = api_key
    openai.api_base = MODEL_CONFIGS["openai"]["url"]
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
            response = openai.ChatCompletion.create(**body, stream=True)
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
    # ... (rest of the grok_proxy code)
