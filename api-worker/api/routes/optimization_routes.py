"""Optimization workflow API routes."""
from fastapi import APIRouter, HTTPException, status

from models.api_models import OptimizationTriggerRequest, OptimizationTriggerResponse
from controller.optimization_controller import OptimizationController

router = APIRouter()
controller = OptimizationController()


@router.post("/optimization/trigger", response_model=OptimizationTriggerResponse)
async def trigger_optimization(request: OptimizationTriggerRequest):
    """Manually trigger the prompt optimization workflow."""
    try:
        return await controller.trigger_optimization(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger optimization: {str(e)}"
        )


@router.get("/optimization/status/{workflow_id}")
async def get_optimization_status(workflow_id: str):
    """Get the status of an optimization workflow."""
    try:
        return await controller.get_optimization_status(workflow_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow status: {str(e)}"
        )
