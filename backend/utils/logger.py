"""
Logger module for the Thinking AI Model Comparison Platform.

This module provides a comprehensive logging system with:
- Different log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Log rotation by date
- Separate log files for different log types
- Colorized console output
- JSON formatting for machine-readable logs
"""

import os
import sys
import json
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
import uuid

# Import environment configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from env_config import get_log_level, get_env_variable

# ANSI color codes for colorized console output
COLORS = {
    'DEBUG': '\033[36m',     # Cyan
    'INFO': '\033[32m',      # Green
    'WARNING': '\033[33m',   # Yellow
    'ERROR': '\033[31m',     # Red
    'CRITICAL': '\033[41m',  # Red background
    'RESET': '\033[0m'       # Reset to default
}

# Determine environment from .env file
ENVIRONMENT = get_env_variable("ENVIRONMENT", "development")

# Set logs directory based on environment
if ENVIRONMENT.lower() == "production":
    # In production, use a directory outside the deployment path
    LOGS_DIR = Path("/home/thinking/logs")
else:
    # In development, use a directory in the project
    LOGS_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Define log file paths
REQUEST_LOG_PATH = LOGS_DIR / "requests"
ERROR_LOG_PATH = LOGS_DIR / "errors"
APP_LOG_PATH = LOGS_DIR / "app"
ARCHIVE_LOG_PATH = LOGS_DIR / "archived"

# Create log directories if they don't exist
REQUEST_LOG_PATH.mkdir(exist_ok=True)
ERROR_LOG_PATH.mkdir(exist_ok=True)
APP_LOG_PATH.mkdir(exist_ok=True)
ARCHIVE_LOG_PATH.mkdir(exist_ok=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to console logs."""
    
    def format(self, record):
        levelname = record.levelname
        if levelname in COLORS:
            record.levelname = f"{COLORS[levelname]}{levelname}{COLORS['RESET']}"
        return super().format(record)

class JsonFormatter(logging.Formatter):
    """Custom formatter to output logs in JSON format."""
    
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
        }
        
        # Add exception info if available
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
            
        # Add extra fields if available
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
            
        return json.dumps(log_data)

def get_logger(name: str, 
               log_level: Optional[str] = None) -> logging.Logger:
    """
    Get a logger with the specified name and configuration.
    
    Args:
        name: The name of the logger
        log_level: Override the default log level from environment
        
    Returns:
        A configured logger instance
    """
    # Get log level from environment if not specified
    if log_level is None:
        log_level = get_log_level()
    
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # Clear existing handlers if any
    if logger.handlers:
        logger.handlers.clear()
    
    # Create console handler with colored output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Create file handler for general app logs with rotation
    app_handler = logging.handlers.TimedRotatingFileHandler(
        APP_LOG_PATH / f"{name}.log",
        when='midnight',
        backupCount=30  # Keep logs for 30 days
    )
    app_handler.setLevel(numeric_level)
    app_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    app_handler.setFormatter(app_formatter)
    logger.addHandler(app_handler)
    
    # Create file handler for error logs with rotation
    error_handler = logging.handlers.TimedRotatingFileHandler(
        ERROR_LOG_PATH / f"{name}_error.log",
        when='midnight',
        backupCount=90  # Keep error logs for 90 days
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s\n'
        'Path: %(pathname)s:%(lineno)d\n'
        'Function: %(funcName)s\n'
        '%(exc_info)s\n',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    error_handler.setFormatter(error_formatter)
    logger.addHandler(error_handler)
    
    return logger

def get_request_logger() -> logging.Logger:
    """
    Get a specialized logger for HTTP requests.
    
    Returns:
        A configured logger instance for requests
    """
    logger = logging.getLogger("thinking.requests")
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers if any
    if logger.handlers:
        logger.handlers.clear()
    
    # Create file handler for request logs with rotation
    request_handler = logging.handlers.TimedRotatingFileHandler(
        REQUEST_LOG_PATH / "requests.log",
        when='midnight',
        backupCount=30  # Keep request logs for 30 days
    )
    request_handler.setLevel(logging.INFO)
    
    # Use JSON formatter for machine-readable logs
    request_formatter = JsonFormatter()
    request_handler.setFormatter(request_formatter)
    logger.addHandler(request_handler)
    
    return logger

# Create a request logger instance for import
request_logger = get_request_logger()

def log_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
    response_size: Optional[int] = None,
    extra: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log an HTTP request with detailed information.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        path: Request path
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
        user_agent: User agent string
        ip_address: Client IP address
        payload: Request payload (will be sanitized)
        response_size: Size of the response in bytes
        extra: Additional fields to include in the log
    """
    # Generate a unique request ID
    request_id = str(uuid.uuid4())
    
    # Sanitize payload to remove sensitive information
    sanitized_payload = None
    if payload:
        sanitized_payload = sanitize_payload(payload)
    
    # Prepare log record
    log_data = {
        'request_id': request_id,
        'method': method,
        'path': path,
        'status_code': status_code,
        'duration_ms': duration_ms,
        'user_agent': user_agent,
        'ip_address': ip_address,
        'payload': sanitized_payload,
        'response_size': response_size
    }
    
    # Add extra fields if provided
    if extra:
        log_data['extra'] = extra
    
    # Create a LogRecord with extra data
    record = logging.LogRecord(
        name="thinking.requests",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg=f"{method} {path} {status_code} {duration_ms}ms",
        args=(),
        exc_info=None
    )
    record.extra = log_data
    
    # Log the record
    for handler in request_logger.handlers:
        handler.handle(record)

def sanitize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize request payload to remove sensitive information.
    
    Args:
        payload: The original payload
        
    Returns:
        A sanitized copy of the payload
    """
    # Create a deep copy to avoid modifying the original
    sanitized = {}
    
    # List of sensitive fields to redact
    sensitive_fields = [
        'api_key', 'apiKey', 'api_keys', 'apiKeys', 'key', 'token', 'secret',
        'password', 'credentials', 'authorization', 'auth'
    ]
    
    # Recursively sanitize the payload
    def _sanitize(obj):
        if isinstance(obj, dict):
            result = {}
            for k, v in obj.items():
                # Check if this is a sensitive field
                if any(field in k.lower() for field in sensitive_fields):
                    result[k] = "[REDACTED]"
                else:
                    result[k] = _sanitize(v)
            return result
        elif isinstance(obj, list):
            return [_sanitize(item) for item in obj]
        else:
            return obj
    
    return _sanitize(payload)

def archive_old_logs(days_to_keep: int = 30) -> None:
    """
    Archive logs older than the specified number of days.
    
    Args:
        days_to_keep: Number of days to keep logs before archiving
    """
    import shutil
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    archive_date = datetime.now().strftime("%Y%m%d")
    
    # Create archive directory for this run
    archive_dir = ARCHIVE_LOG_PATH / archive_date
    archive_dir.mkdir(exist_ok=True)
    
    # Function to check if a log file is older than cutoff date
    def is_old_log(file_path):
        # Parse date from filename (assuming format like app.log.2025-04-01)
        try:
            if '.log.' in file_path.name:
                date_str = file_path.name.split('.log.')[1]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                return file_date < cutoff_date
            return False
        except (ValueError, IndexError):
            return False
    
    # Archive old logs from each directory
    for log_dir in [APP_LOG_PATH, REQUEST_LOG_PATH, ERROR_LOG_PATH]:
        for log_file in log_dir.glob("*.log.*"):
            if is_old_log(log_file):
                # Create subdirectory in archive matching original structure
                target_dir = archive_dir / log_dir.name
                target_dir.mkdir(exist_ok=True)
                
                # Move file to archive
                shutil.move(str(log_file), str(target_dir / log_file.name))
    
    # Compress the archive directory
    if any(archive_dir.iterdir()):
        shutil.make_archive(str(archive_dir), 'gzip', str(archive_dir))
        # Remove the uncompressed directory after creating archive
        shutil.rmtree(str(archive_dir))

# Create a default app logger
logger = get_logger("thinking")
