from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import os
import time
import sys

# Add the parent directory to path for imports to work when running from backend/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

# Try relative imports first, then fall back to absolute imports
try:
    # For running as python -m backend.main from project root
    from env_config import (
        get_api_key, get_api_url, get_model, get_server_config,
        get_current_env, switch_environment, get_log_level,
        ENV_DEV, ENV_TEST, ENV_PRD
    )
    from utils.logger import logger, archive_old_logs
    from utils.middleware import RequestLoggingMiddleware
    from routers.chat import chat_router
    from routers.discuss import discuss_router
    print("Using relative imports")
except ImportError:
    # For running with uvicorn from project root
    from backend.env_config import (
        get_api_key, get_api_url, get_model, get_server_config,
        get_current_env, switch_environment, get_log_level,
        ENV_DEV, ENV_TEST, ENV_PRD
    )
    from backend.utils.logger import logger, archive_old_logs
    from backend.utils.middleware import RequestLoggingMiddleware
    from backend.routers.chat import chat_router
    from backend.routers.discuss import discuss_router
    print("Using absolute imports")

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

# Register routers
app.include_router(chat_router)
app.include_router(discuss_router)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Check if the API is running and return status"""
    return {
        "status": "ok",
        "environment": get_current_env(),
        "version": "1.0.0"
    }

# Admin endpoints for configuration and monitoring
@app.get("/api/admin/log-level")
async def get_current_log_level():
    """Get the current log level"""
    return {"level": get_log_level()}

@app.post("/api/admin/log-level/{level}")
async def set_log_level(level: str):
    """Set the log level"""
    # Validate the log level
    if level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        raise HTTPException(status_code=400, detail=f"Invalid log level: {level}")
        
    # Set the log level
    logger.setLevel(level)
    logger.info(f"Log level changed to {level}")
    
    return {"level": level, "status": "updated"}

# Configuration endpoints
@app.post("/api/admin/config/reload")
async def reload_config():
    """Reload configuration from environment variables"""
    # Re-read environment variables
    os.environ["CONFIG_RELOAD_TIMESTAMP"] = str(int(time.time()))
    
    # Log configuration reload
    logger.info("Configuration reloaded from environment variables")
    
    # Return success status
    return {"status": "reloaded"}

@app.post("/api/admin/env/{env}")
async def change_environment(env: str):
    """Change the current environment"""
    if env not in [ENV_DEV, ENV_TEST, ENV_PRD]:
        raise HTTPException(status_code=400, detail=f"Invalid environment: {env}")
    
    # Switch environment
    switch_environment(env)
    logger.info(f"Environment changed to {env}")
    
    return {"environment": env, "status": "updated"}

@app.get("/api/admin/env")
async def get_environment():
    """Get the current environment"""
    return {"environment": get_current_env()}

# Startup configuration
if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Get environment from command line if provided
    if len(sys.argv) > 1 and sys.argv[1] in [ENV_DEV, ENV_TEST, ENV_PRD]:
        env = sys.argv[1]
        logger.info(f"Setting environment to {env} from command line")
        switch_environment(env)
    
    # Get server configuration
    host = get_server_config("host", "0.0.0.0")
    port = int(get_server_config("port", 8000))
    
    # Start the server
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=get_current_env() == ENV_DEV)
