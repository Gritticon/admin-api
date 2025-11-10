"""
CloudWatch-Optimized Logging Configuration
Structured JSON logging for AWS CloudWatch via ECS.
"""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
from core.config import settings


class CloudWatchJSONFormatter(logging.Formatter):
    """JSON formatter optimized for CloudWatch Logs Insights."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON for CloudWatch."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "path"):
            log_data["path"] = record.path
        if hasattr(record, "method"):
            log_data["method"] = record.method
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        
        # Add any other extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs", "message",
                "pathname", "process", "processName", "relativeCreated", "thread",
                "threadName", "exc_info", "exc_text", "stack_info"
            ]:
                log_data[key] = value
        
        return json.dumps(log_data)


def setup_logging():
    """
    Configure structured JSON logging for CloudWatch.
    Logs are sent to stdout/stderr which ECS automatically captures.
    """
    # JSON formatter for CloudWatch
    json_formatter = CloudWatchJSONFormatter()
    
    # Console handler (stdout) - ECS captures this automatically
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    root_logger.addHandler(console_handler)
    
    # Remove any existing handlers to avoid duplicates
    root_logger.handlers = [console_handler]
    
    # Set levels for third-party libraries (reduce noise in CloudWatch)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Usage:
        logger = get_logger(__name__)
        logger.info("Operation completed", extra={"user_id": 123})
    """
    return logging.getLogger(name)

