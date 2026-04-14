"""Prompt management API routes."""
from typing import List
from fastapi import APIRouter, HTTPException, status

from models.api_models import PromptResponse, PromotePromptRequest
from controller.prompt_controller import PromptController

router = APIRouter()
controller = PromptController()


@router.get("/prompts/active", response_model=List[PromptResponse])
async def get_active_prompts():
    """Get all active prompts."""
    try:
        return await controller.get_active_prompts()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch active prompts: {str(e)}"
        )


@router.get("/prompts/experimental", response_model=List[PromptResponse])
async def get_experimental_prompts(limit: int = 50):
    """Get all experimental prompts."""
    try:
        return await controller.get_experimental_prompts(limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch experimental prompts: {str(e)}"
        )


@router.get("/prompts/experimental/top", response_model=List[PromptResponse])
async def get_top_experimental_prompts(limit: int = 10):
    """Get top-performing experimental prompts."""
    try:
        return await controller.get_top_experimental_prompts(limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch top experimental prompts: {str(e)}"
        )


@router.post("/prompts/promote")
async def promote_experimental_prompt(request: PromotePromptRequest):
    """Promote an experimental prompt to active status."""
    try:
        return await controller.promote_prompt(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Promotion failed: {str(e)}"
        )
