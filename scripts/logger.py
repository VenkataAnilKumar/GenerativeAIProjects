"""
Structured Logging Module
Provides JSON-formatted logging for all use cases with request tracking.
"""

import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import uuid


class StructuredLogger:
    """
    JSON-structured logger for tracking AI requests and responses.
    
    Usage:
        logger = StructuredLogger("marketing_content")
        req_id = logger.log_request(prompt="Generate email", mode="demo")
        logger.log_response(req_id, tokens=100, cost=0.002, latency_ms=1500)
    """

    def __init__(self, use_case: str, log_level: str = "INFO"):
        self.use_case = use_case
        self.logger = logging.getLogger(use_case)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set level
        self.logger.setLevel(getattr(logging, log_level))
        
        # Create JSON formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
        
        # Don't propagate to root
        self.logger.propagate = False

    def log_request(
        self,
        prompt: str,
        mode: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Log an incoming request. Returns unique request ID."""
        request_id = str(uuid.uuid4())
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "use_case": self.use_case,
            "request_id": request_id,
            "event": "request_start",
            "mode": mode,
            "prompt_length": len(prompt),
            "user_id": user_id or "anonymous",
        }
        
        if metadata:
            log_data["metadata"] = metadata
        
        self.logger.info(json.dumps(log_data))
        return request_id

    def log_response(
        self,
        request_id: str,
        tokens: int = 0,
        cost: float = 0.0,
        latency_ms: float = 0.0,
        success: bool = True,
        error: Optional[str] = None,
    ):
        """Log a completed response."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "use_case": self.use_case,
            "request_id": request_id,
            "event": "request_end",
            "tokens": tokens,
            "cost_usd": round(cost, 6),
            "latency_ms": round(latency_ms, 2),
            "success": success,
        }
        
        if error:
            log_data["error"] = error
        
        level = logging.INFO if success else logging.ERROR
        self.logger.log(level, json.dumps(log_data))

    def log_error(self, request_id: str, error: str, stacktrace: Optional[str] = None):
        """Log an error event."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "use_case": self.use_case,
            "request_id": request_id,
            "event": "error",
            "error": error,
        }
        
        if stacktrace:
            log_data["stacktrace"] = stacktrace
        
        self.logger.error(json.dumps(log_data))


class JSONFormatter(logging.Formatter):
    """Custom formatter for JSON logs."""

    def format(self, record):
        """Format log record as JSON if not already."""
        message = record.getMessage()
        
        # If already JSON, return as-is
        try:
            json.loads(message)
            return message
        except (json.JSONDecodeError, TypeError):
            # Otherwise wrap in JSON structure
            return json.dumps({
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": message,
            })


def get_logger(use_case: str) -> StructuredLogger:
    """Factory function to get a logger instance."""
    return StructuredLogger(use_case)
