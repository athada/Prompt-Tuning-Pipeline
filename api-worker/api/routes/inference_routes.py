"""Inference API routes."""
from fastapi import APIRouter, HTTPException, status

from models.api_models import InferenceRequest, InferenceResponse
from controller.inference_controller import InferenceController

router = APIRouter()
controller = InferenceController()


@router.post("/inference", response_model=InferenceResponse)
async def run_inference(request: InferenceRequest):
    """Run inference using active or experimental prompts."""
    try:
        return await controller.run_inference(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "prompt-tuning-api",
        "version": "1.0.0"
    }
