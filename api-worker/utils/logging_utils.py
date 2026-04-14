"""Utility functions for logging."""
import logging
from typing import Any, Dict


def log_activity_start(activity_name: str, **kwargs):
    """Log the start of an activity."""
    logger = logging.getLogger(activity_name)
    logger.info(f"Starting activity: {activity_name}", extra=kwargs)


def log_activity_end(activity_name: str, result: Any):
    """Log the end of an activity."""
    logger = logging.getLogger(activity_name)
    logger.info(f"Completed activity: {activity_name}", extra={"result": str(result)[:100]})


def log_activity_error(activity_name: str, error: Exception):
    """Log an activity error."""
    logger = logging.getLogger(activity_name)
    logger.error(f"Activity failed: {activity_name}", exc_info=error)
