"""
Main entrypoint for the Thinking backend API.
"""
import os
import sys
import time
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Add the parent directory to sys.path for direct execution
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Handle imports for both direct execution and module imports
try:
    # When running as a module
    from backend.env_config import (
        get_current_env, get_log_level, ENV_DEV, ENV_TEST, ENV_PRD,
        switch_environment, get_server_config
    )
    from backend.routers.chat import chat_router
    from backend.routers.discuss import discuss_router
    from backend.utils.logger import logger, archive_old_logs
    from backend.utils.middleware import RequestLoggingMiddleware
except ImportError:
    # When running directly
    from env_config import (
        get_current_env, get_log_level, ENV_DEV, ENV_TEST, ENV_PRD,
        switch_environment, get_server_config
    )
    from routers.chat import chat_router
    from routers.discuss import discuss_router
    from utils.logger import logger, archive_old_logs
    from utils.middleware import RequestLoggingMiddleware

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

@app.get("/api/health")
async def health_check():
    """Check if the API is running and return status."""
    return {
        "status": "ok",
        "environment": get_current_env(),
        "version": "1.0.0"
    }

@app.get("/api/admin/log-level")
async def get_current_log_level():
    """Get the current log level."""
    return {"level": get_log_level()}

@app.post("/api/admin/log-level/{level}")
async def set_log_level(level: str):
    """Set the log level."""
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if level not in valid_levels:
        raise HTTPException(status_code=400, detail=f"Invalid log level: {level}")
    logger.setLevel(level)
    logger.info(f"Log level changed to {level}")
    return {"level": level, "status": "updated"}

@app.post("/api/admin/config/reload")
async def reload_config():
    """Reload configuration from environment variables."""
    os.environ["CONFIG_RELOAD_TIMESTAMP"] = str(int(time.time()))
    logger.info("Configuration reloaded from environment variables")
    return {"status": "reloaded"}

@app.post("/api/admin/env/{env}")
async def change_environment(env: str):
    """Change the current environment."""
    if env not in [ENV_DEV, ENV_TEST, ENV_PRD]:
        raise HTTPException(status_code=400, detail=f"Invalid environment: {env}")
    
    # Switch environment
    switch_environment(env)
    logger.info(f"Environment changed to {env}")
    
    return {"environment": env, "status": "updated"}

@app.get("/api/admin/env")
async def get_environment():
    """Get the current environment."""
    return {"environment": get_current_env()}

# Startup configuration
if __name__ == "__main__":
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
    # Use the appropriate module path based on how the script is being run
    module_path = "main:app" if os.path.basename(sys.argv[0]) == "main.py" else "backend.main:app"
    uvicorn.run(module_path, host=host, port=port, reload=get_current_env() == ENV_DEV)
