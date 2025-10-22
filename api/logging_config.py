"""
Logging Configuration for AI-Studio API

Provides structured logging with file and console output for tracking
application errors, background task failures, and system events.

Features:
- Structured JSON logging for production
- Request ID correlation
- Colored console output for development
- Rotating file handlers
"""

import logging
import sys
import json
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional
import contextvars

# Context variable to store request ID for log correlation
request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('request_id', default=None)


class StructuredFormatter(logging.Formatter):
    """
    JSON formatter for structured logging

    Includes request_id from context for log correlation
    """

    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }

        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            log_data['request_id'] = request_id

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add any extra fields
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


class ColoredConsoleFormatter(logging.Formatter):
    """
    Colored console formatter for development

    Uses ANSI color codes for better readability
    """

    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)

        # Format: [INFO] module.function: message (request_id)
        parts = [f"{color}{record.levelname:8}{self.RESET}"]

        # Add logger name if not root
        if record.name and record.name != 'root':
            parts.append(f"{record.name}:")

        # Add message
        parts.append(record.getMessage())

        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            parts.append(f"(req:{request_id[:8]})")

        return " ".join(parts)


def setup_logging(log_dir: Path = None, log_level: str = "INFO", structured: bool = False):
    """
    Configure application-wide logging

    Args:
        log_dir: Directory for log files (default: ./logs)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        structured: Use JSON structured logging (for production)
    """
    # Create logs directory
    if log_dir is None:
        log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Console handler with colored output (development) or JSON (production)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    if structured:
        console_handler.setFormatter(StructuredFormatter())
    else:
        console_handler.setFormatter(ColoredConsoleFormatter())

    # File handler for all logs (structured JSON)
    all_logs_handler = RotatingFileHandler(
        log_dir / "api.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    all_logs_handler.setLevel(logging.DEBUG)
    all_logs_handler.setFormatter(StructuredFormatter())

    # File handler for errors only (structured JSON)
    error_handler = RotatingFileHandler(
        log_dir / "errors.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(StructuredFormatter())

    # File handler for background tasks (structured JSON)
    background_handler = RotatingFileHandler(
        log_dir / "background_tasks.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    background_handler.setLevel(logging.DEBUG)
    background_handler.setFormatter(StructuredFormatter())

    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(all_logs_handler)
    root_logger.addHandler(error_handler)

    # Create background task logger
    background_logger = logging.getLogger("background_tasks")
    background_logger.addHandler(background_handler)
    background_logger.setLevel(logging.DEBUG)

    # Use logger instead of print for logging messages
    logger = logging.getLogger("life_os.setup")
    logger.info(f"Logging configured: {log_dir}/")
    logger.info(f"  - All logs: api.log (JSON)")
    logger.info(f"  - Errors: errors.log (JSON)")
    logger.info(f"  - Background tasks: background_tasks.log (JSON)")
    logger.info(f"  - Console output: {'JSON' if structured else 'Colored'}")


def get_background_logger():
    """Get logger for background tasks"""
    return logging.getLogger("background_tasks")


def set_request_id(request_id: str):
    """Set request ID in context for log correlation"""
    request_id_var.set(request_id)


def get_request_id() -> Optional[str]:
    """Get current request ID from context"""
    return request_id_var.get()


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(name)
    return logging.getLogger()


def log_with_context(logger: logging.Logger, level: str, message: str, **context):
    """
    Log message with additional context fields

    Args:
        logger: Logger instance
        level: Log level (info, error, warning, debug)
        message: Log message
        **context: Additional fields to include in structured logs
    """
    # Create a log record with extra fields
    log_func = getattr(logger, level.lower())

    # For structured logging, attach extra fields to the record
    if context:
        # Create a custom LogRecord with extra_fields
        old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.extra_fields = context
            return record

        logging.setLogRecordFactory(record_factory)
        log_func(message)
        logging.setLogRecordFactory(old_factory)
    else:
        log_func(message)


def log_background_task_start(task_name: str, **kwargs):
    """
    Log the start of a background task

    Args:
        task_name: Name of the task
        **kwargs: Additional context to log
    """
    logger = get_background_logger()
    log_with_context(logger, 'info', f"Starting background task: {task_name}", task=task_name, **kwargs)


def log_background_task_success(task_name: str, duration_ms: float = None, **kwargs):
    """
    Log successful completion of a background task

    Args:
        task_name: Name of the task
        duration_ms: Task duration in milliseconds
        **kwargs: Additional context to log
    """
    logger = get_background_logger()
    context = {'task': task_name, **kwargs}
    if duration_ms:
        context['duration_ms'] = duration_ms
    log_with_context(logger, 'info', f"Completed background task: {task_name}", **context)


def log_background_task_error(task_name: str, error: Exception, **kwargs):
    """
    Log background task failure

    Args:
        task_name: Name of the task
        error: Exception that occurred
        **kwargs: Additional context to log
    """
    logger = get_background_logger()
    logger.error(
        f"Background task failed: {task_name}",
        exc_info=error,
        extra={'extra_fields': {'task': task_name, 'error_type': type(error).__name__, **kwargs}}
    )
