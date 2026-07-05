from typing import Optional, Any, Dict
from fastapi import Request
from fastapi.responses import JSONResponse
from quantum_os.core.config import settings
from quantum_os.core.logging import log

class QuantumOSException(Exception):
    """Base exception for QuantumOS"""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class DatabaseError(QuantumOSException):
    """Database operation errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)

class NotFoundError(QuantumOSException):
    """Resource not found"""
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)

class ValidationError(QuantumOSException):
    """Input validation errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)

class AuthenticationError(QuantumOSException):
    """Authentication errors"""
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, details=details)

class AuthorizationError(QuantumOSException):
    """Authorization errors"""
    def __init__(self, message: str = "Not authorized", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, details=details)

async def quantumos_exception_handler(request: Request, exc: QuantumOSException):
    """Handle QuantumOS exceptions"""
    log.error(f"QuantumOS Exception: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "status_code": exc.status_code
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Handle generic exceptions"""
    log.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "details": {"message": str(exc)} if settings.DEBUG else {}
        }
    )
