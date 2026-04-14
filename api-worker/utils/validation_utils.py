"""Utility functions for validation."""
from typing import Any, Dict


def validate_score(score: float) -> bool:
    """Validate that a score is between 0 and 10."""
    return 0.0 <= score <= 10.0


def validate_prompt_text(text: str) -> bool:
    """Validate that prompt text is not empty."""
    return bool(text and text.strip())


def validate_agent_name(name: str) -> bool:
    """Validate agent name format."""
    return bool(name and name.strip() and "_" not in name or name.replace("_", "").isalnum())
