"""Evaluation API routes."""
from typing import List
from fastapi import APIRouter, HTTPException, status

from models.api_models import EvaluationLogResponse
from controller.evaluation_controller import EvaluationController

router = APIRouter()
controller = EvaluationController()


@router.get("/evaluations/recent", response_model=List[EvaluationLogResponse])
async def get_recent_evaluations(limit: int = 100):
    """Get recent evaluation logs."""
    try:
        return await controller.get_recent_evaluations(limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch evaluations: {str(e)}"
        )


@router.get("/evaluations/prompt/{prompt_id}", response_model=List[EvaluationLogResponse])
async def get_evaluations_for_prompt(prompt_id: str, limit: int = 50):
    """Get evaluation logs for a specific prompt."""
    try:
        return await controller.get_evaluations_for_prompt(prompt_id, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch evaluations for prompt: {str(e)}"
        )
