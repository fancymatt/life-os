"""
Logging Configuration for AI-Studio API

Provides structured logging with file and console output for tracking
application errors, background task failures, and system events.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logging(log_dir: Path = None, log_level: str = "INFO"):
    """
    Configure application-wide logging

    Args:
        log_dir: Directory for log files (default: ./logs)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
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

    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(levelname)s:     %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # File handler for all logs (rotating)
    all_logs_handler = RotatingFileHandler(
        log_dir / "api.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    all_logs_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    all_logs_handler.setFormatter(file_formatter)

    # File handler for errors only (rotating)
    error_handler = RotatingFileHandler(
        log_dir / "errors.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)

    # File handler for background tasks (rotating)
    background_handler = RotatingFileHandler(
        log_dir / "background_tasks.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    background_handler.setLevel(logging.DEBUG)
    background_handler.setFormatter(file_formatter)

    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(all_logs_handler)
    root_logger.addHandler(error_handler)

    # Create background task logger
    background_logger = logging.getLogger("background_tasks")
    background_logger.addHandler(background_handler)
    background_logger.setLevel(logging.DEBUG)

    print(f"✅ Logging configured: {log_dir}/")
    print(f"   - All logs: api.log")
    print(f"   - Errors: errors.log")
    print(f"   - Background tasks: background_tasks.log")


def get_background_logger():
    """Get logger for background tasks"""
    return logging.getLogger("background_tasks")


def log_background_task_start(task_name: str, **kwargs):
    """
    Log the start of a background task

    Args:
        task_name: Name of the task
        **kwargs: Additional context to log
    """
    logger = get_background_logger()
    context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.info(f"Starting background task: {task_name} | {context}")


def log_background_task_success(task_name: str, duration_ms: float = None, **kwargs):
    """
    Log successful completion of a background task

    Args:
        task_name: Name of the task
        duration_ms: Task duration in milliseconds
        **kwargs: Additional context to log
    """
    logger = get_background_logger()
    context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
    duration_str = f" | duration={duration_ms:.2f}ms" if duration_ms else ""
    logger.info(f"Completed background task: {task_name}{duration_str} | {context}")


def log_background_task_error(task_name: str, error: Exception, **kwargs):
    """
    Log background task failure

    Args:
        task_name: Name of the task
        error: Exception that occurred
        **kwargs: Additional context to log
    """
    logger = get_background_logger()
    context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.error(
        f"Background task failed: {task_name} | {context}",
        exc_info=error
    )
