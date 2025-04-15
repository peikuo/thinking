"""
Middleware module for the Thinking API.

This module provides middleware components for the FastAPI application,
including request logging, error handling, and more.
"""

import time
import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
from typing import Callable, Dict, Any, Optional

from utils.logger import log_request, logger

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    
    This middleware logs details about each request including:
    - HTTP method
    - Path
    - Status code
    - Duration
    - User agent
    - IP address
    - Request payload (sanitized)
    - Response size
    """
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Record request start time
        start_time = time.time()
        
        # Get request details
        method = request.method
        path = request.url.path
        user_agent = request.headers.get("user-agent")
        client_ip = request.client.host if request.client else None
        
        # Get request body (if applicable)
        payload = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                # Make a copy of the request body
                body = await request.body()
                if body:
                    # Reset the request body for downstream handlers
                    request._body = body
                    try:
                        # Try to parse as JSON
                        payload = json.loads(body)
                    except json.JSONDecodeError:
                        # If not JSON, just note the content type
                        payload = {"content_type": request.headers.get("content-type", "unknown")}
            except Exception as e:
                logger.warning(f"Error reading request body: {str(e)}")
        
        # Process the request
        response = None
        status_code = 500  # Default in case of unhandled exceptions
        response_size = 0
        
        try:
            # Call the next middleware/endpoint
            response = await call_next(request)
            status_code = response.status_code
            
            # Get response size if possible
            if hasattr(response, "body"):
                response_size = len(response.body)
            
            return response
        except Exception as e:
            # Log exceptions
            logger.exception(f"Unhandled exception in request: {str(e)}")
            raise
        finally:
            # Calculate request duration
            duration_ms = round((time.time() - start_time) * 1000, 2)
            
            # Log the request
            log_request(
                method=method,
                path=path,
                status_code=status_code,
                duration_ms=duration_ms,
                user_agent=user_agent,
                ip_address=client_ip,
                payload=payload,
                response_size=response_size,
                extra={
                    "environment": "production" if path.startswith("/api/") else "development"
                }
            )
