"""Workflow service - handles workflow execution."""
from temporalio.client import Client, WorkflowHandle

from config import settings
from service.temporal_service import temporal_service
from service.workflows import PromptOptimizationWorkflow


class WorkflowService:
    """Service for workflow operations."""
    
    async def start_optimization_workflow(
        self,
        workflow_id: str,
        batch_size: int = None
    ) -> WorkflowHandle:
        """Start a prompt optimization workflow."""
        client = temporal_service.get_client()
        
        handle = await client.start_workflow(
            PromptOptimizationWorkflow.run,
            args=[batch_size or settings.batch_size],
            id=workflow_id,
            task_queue=settings.temporal_task_queue
        )
        
        return handle
    
    async def get_workflow_status(self, workflow_id: str) -> dict:
        """Get the status of a workflow."""
        client = temporal_service.get_client()
        handle = client.get_workflow_handle(workflow_id)
        
        try:
            result = await handle.result()
            return {
                "status": "completed",
                "workflow_id": workflow_id,
                "result": result
            }
        except:
            return {
                "status": "running",
                "workflow_id": workflow_id,
                "message": "Workflow is still running"
            }
