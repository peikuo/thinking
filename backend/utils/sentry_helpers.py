"""
Sentry helper functions for error tracking and monitoring.

This module provides utility functions for working with Sentry in the application.
"""

import asyncio
import functools
import logging
from typing import Any, Callable, Dict, Optional, TypeVar, cast

import sentry_sdk

# Type variables for function signatures
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

# Get logger
logger = logging.getLogger(__name__)

def capture_exception(error: Exception, extra_context: Optional[Dict[str, Any]] = None) -> None:
    """
    Capture an exception and send it to Sentry with optional extra context.
    
    Args:
        error: The exception to capture
        extra_context: Additional context to include with the error
    """
    if extra_context:
        with sentry_sdk.configure_scope() as scope:
            for key, value in extra_context.items():
                scope.set_extra(key, value)
    
    sentry_sdk.capture_exception(error)
    logger.error(f"Exception captured and sent to Sentry: {str(error)}")

def track_errors(func: F) -> F:
    """
    Decorator to automatically track exceptions in a function and send them to Sentry.
    Works with both synchronous and asynchronous functions.
    
    Example:
        @track_errors
        def my_function():
            # This function will have all exceptions sent to Sentry
            pass
            
        @track_errors
        async def my_async_function():
            # This async function will also have exceptions sent to Sentry
            pass
    
    Args:
        func: The function to wrap
        
    Returns:
        The wrapped function
    """
    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Add context about the function
            extra_context = {
                "function": func.__name__,
                "module": func.__module__,
                # Avoid serialization issues with complex objects
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys())
            }
            capture_exception(e, extra_context)
            # Re-raise the exception after capturing
            raise
    
    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Add context about the function
            extra_context = {
                "function": func.__name__,
                "module": func.__module__,
                # Avoid serialization issues with complex objects
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys())
            }
            capture_exception(e, extra_context)
            # Re-raise the exception after capturing
            raise
    
    # Determine if the function is a coroutine function and return the appropriate wrapper
    if asyncio.iscoroutinefunction(func):
        return cast(F, async_wrapper)
    return cast(F, sync_wrapper)

def set_user_context(user_id: str, email: Optional[str] = None, username: Optional[str] = None) -> None:
    """
    Set user context for Sentry events.
    
    Args:
        user_id: Unique identifier for the user
        email: User's email address (optional)
        username: User's username (optional)
    """
    user_context = {"id": user_id}
    if email:
        user_context["email"] = email
    if username:
        user_context["username"] = username
        
    sentry_sdk.set_user(user_context)
    logger.debug(f"Set Sentry user context for user {user_id}")

def clear_user_context() -> None:
    """
    Clear the current user context from Sentry.
    """
    sentry_sdk.set_user(None)
    logger.debug("Cleared Sentry user context")

def set_tag(key: str, value: str) -> None:
    """
    Set a tag for all subsequent Sentry events.
    
    Args:
        key: Tag name
        value: Tag value
    """
    sentry_sdk.set_tag(key, value)
    logger.debug(f"Set Sentry tag {key}={value}")
