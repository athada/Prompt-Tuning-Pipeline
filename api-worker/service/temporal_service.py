"""Temporal service - manages Temporal worker lifecycle."""
import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker

from config import settings
from service.workflow_activities import (
    fetch_recent_low_score_evaluations,
    evaluate_prompt_performance,
    generate_improved_prompt,
    test_experimental_prompt,
    get_active_prompt_info
)
from service.workflows import PromptOptimizationWorkflow, PeriodicOptimizationWorkflow

logger = logging.getLogger(__name__)


class TemporalService:
    """Service for Temporal worker management."""
    
    def __init__(self):
        self.client: Client = None
        self.worker_task: asyncio.Task = None
    
    async def start_worker(self):
        """Start the Temporal worker."""
        self.worker_task = asyncio.create_task(self._run_worker())
    
    async def stop_worker(self):
        """Stop the Temporal worker."""
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
    
    async def _run_worker(self):
        """Run the Temporal worker."""
        try:
            # Connect to Temporal
            self.client = await Client.connect(settings.temporal_host)
            logger.info(f"Connected to Temporal at {settings.temporal_host}")
            
            # Create worker
            worker = Worker(
                self.client,
                task_queue=settings.temporal_task_queue,
                workflows=[PromptOptimizationWorkflow, PeriodicOptimizationWorkflow],
                activities=[
                    fetch_recent_low_score_evaluations,
                    evaluate_prompt_performance,
                    generate_improved_prompt,
                    test_experimental_prompt,
                    get_active_prompt_info
                ],
            )
            
            logger.info(f"Worker listening on task queue: {settings.temporal_task_queue}")
            
            # Run worker
            await worker.run()
            
        except asyncio.CancelledError:
            logger.info("Temporal worker cancelled")
        except Exception as e:
            logger.error(f"Temporal worker error: {e}", exc_info=True)
    
    def get_client(self) -> Client:
        """Get the Temporal client."""
        if not self.client:
            raise RuntimeError("Temporal client not connected")
        return self.client


# Global Temporal service instance
temporal_service = TemporalService()
