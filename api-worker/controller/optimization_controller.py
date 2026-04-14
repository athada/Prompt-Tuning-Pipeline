"""Optimization controller - handles workflow triggers."""
import time
from temporalio.client import Client

from config import settings
from models.api_models import OptimizationTriggerRequest, OptimizationTriggerResponse
from service.workflow_service import WorkflowService


class OptimizationController:
    """Controller for optimization workflow operations."""
    
    def __init__(self):
        self.workflow_service = WorkflowService()
    
    async def trigger_optimization(self, request: OptimizationTriggerRequest) -> OptimizationTriggerResponse:
        """Manually trigger the prompt optimization workflow."""
        workflow_id = f"manual-optimization-{int(time.time())}"
        
        handle = await self.workflow_service.start_optimization_workflow(
            workflow_id=workflow_id,
            batch_size=request.batch_size
        )
        
        return OptimizationTriggerResponse(
            workflow_id=handle.id,
            run_id=handle.result_run_id,
            message="Optimization workflow triggered successfully"
        )
    
    async def get_optimization_status(self, workflow_id: str) -> dict:
        """Get the status of an optimization workflow."""
        return await self.workflow_service.get_workflow_status(workflow_id)
