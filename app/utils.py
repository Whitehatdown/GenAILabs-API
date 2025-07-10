"""
Utility functions and helpers for the API.
"""
import logging
import time
from functools import wraps
from typing import Any, Callable

def timer(func: Callable) -> Callable:
    """Decorator to time function execution."""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    
    return async_wrapper if hasattr(func, '__code__') and func.__code__.co_flags & 0x80 else sync_wrapper

class APIException(Exception):
    """Base exception for API errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ValidationError(APIException):
    """Exception for validation errors."""
    def __init__(self, message: str):
        super().__init__(message, 422)

class NotFoundError(APIException):
    """Exception for not found errors."""
    def __init__(self, message: str):
        super().__init__(message, 404)

class ExternalServiceError(APIException):
    """Exception for external service errors."""
    def __init__(self, message: str):
        super().__init__(message, 503)
