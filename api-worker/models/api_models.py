"""API request/response models."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# API Request/Response Models
# ============================================================================

class InferenceRequest(BaseModel):
    """Request model for running inference."""
    query: str
    use_experimental: bool = False
    prompt_id: Optional[str] = None


class InferenceResponse(BaseModel):
    """Response model for inference results."""
    response: str
    prompt_id: str
    prompt_text: str
    execution_time_ms: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PromptResponse(BaseModel):
    """Response model for prompt data."""
    id: str
    prompt_text: str
    prompt_type: str
    status: str
    created_at: datetime
    performance_score: Optional[float] = None
    test_score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class OptimizationTriggerRequest(BaseModel):
    """Request to manually trigger the optimization workflow."""
    batch_size: Optional[int] = None
    force_regenerate: bool = False


class OptimizationTriggerResponse(BaseModel):
    """Response from triggering optimization."""
    workflow_id: str
    run_id: str
    message: str


class PromotePromptRequest(BaseModel):
    """Request to promote an experimental prompt to active."""
    experimental_prompt_id: str
    archive_old_prompt: bool = True


class EvaluationLogResponse(BaseModel):
    """Response model for evaluation logs."""
    id: str
    prompt_id: str
    input_query: str
    output_response: str
    judge_feedback: str
    judge_score: float
    execution_time_ms: float
    created_at: datetime
