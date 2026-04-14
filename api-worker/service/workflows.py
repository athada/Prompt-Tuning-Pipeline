"""Temporal workflows for prompt optimization."""
from datetime import timedelta
from typing import Dict, Any
import asyncio
from temporalio import workflow
from temporalio.common import RetryPolicy

from config import settings
from service.workflow_activities import (
    fetch_recent_low_score_evaluations,
    evaluate_prompt_performance,
    generate_improved_prompt,
    test_experimental_prompt,
    get_active_prompt_info
)


# ============================================================================
# Workflows
# ============================================================================

@workflow.defn
class PromptOptimizationWorkflow:
    """Main workflow for prompt optimization loop."""
    
    @workflow.run
    async def run(self, batch_size: int = None) -> Dict[str, Any]:
        """Execute the prompt optimization loop."""
        if batch_size is None:
            batch_size = settings.batch_size
        
        workflow.logger.info(f"Starting prompt optimization workflow with batch_size={batch_size}")
        
        # Step 1: Get active prompt info
        active_prompt_info = await workflow.execute_activity(
            get_active_prompt_info,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )
        
        if not active_prompt_info["exists"]:
            workflow.logger.warning("No active prompt found, skipping optimization")
            return {"status": "skipped", "reason": "no_active_prompt"}
        
        # Step 2: Fetch recent low-score evaluations
        low_score_evals = await workflow.execute_activity(
            fetch_recent_low_score_evaluations,
            batch_size,
            start_to_close_timeout=timedelta(seconds=60),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )
        
        if not low_score_evals:
            workflow.logger.info("No low-score evaluations found, prompt is performing well")
            return {"status": "success", "reason": "no_improvements_needed", "evaluations_checked": batch_size}
        
        workflow.logger.info(f"Found {len(low_score_evals)} low-score evaluations")
        
        # Step 3: Generate improved prompt
        experimental_prompt_id = await workflow.execute_activity(
            generate_improved_prompt,
            args=[
                active_prompt_info["id"],
                active_prompt_info["prompt_text"],
                active_prompt_info["agent_name"],
                active_prompt_info["parent_chain"],
                low_score_evals
            ],
            start_to_close_timeout=timedelta(seconds=120),
            retry_policy=RetryPolicy(maximum_attempts=2)
        )
        
        workflow.logger.info(f"Generated experimental prompt: {experimental_prompt_id}")
        
        # Step 4: Test experimental prompt with sample queries
        test_queries = [eval_data["query"] for eval_data in low_score_evals[:5]]
        
        test_results = await workflow.execute_activity(
            test_experimental_prompt,
            args=[experimental_prompt_id, test_queries],
            start_to_close_timeout=timedelta(seconds=180),
            retry_policy=RetryPolicy(maximum_attempts=2)
        )
        
        workflow.logger.info(
            f"Test results - Avg Score: {test_results['average_score']}, "
            f"Original Score: {active_prompt_info['performance_score']}"
        )
        
        # Step 5: Determine if experimental prompt is better
        improvement_found = test_results["average_score"] > active_prompt_info["performance_score"]
        
        return {
            "status": "success",
            "experimental_prompt_id": experimental_prompt_id,
            "test_score": test_results["average_score"],
            "original_score": active_prompt_info["performance_score"],
            "improvement_found": improvement_found,
            "ready_for_promotion": improvement_found and test_results["average_score"] >= settings.score_threshold,
            "low_score_count": len(low_score_evals)
        }


@workflow.defn
class PeriodicOptimizationWorkflow:
    """Workflow that runs optimization on a schedule."""
    
    @workflow.run
    async def run(self) -> None:
        """Run periodic optimization checks."""
        workflow.logger.info("Starting periodic optimization workflow")
        
        while True:
            try:
                # Execute optimization workflow
                result = await workflow.execute_child_workflow(
                    PromptOptimizationWorkflow.run,
                    id=f"optimization-{workflow.now().isoformat()}",
                    task_queue=settings.temporal_task_queue
                )
                
                workflow.logger.info(f"Optimization result: {result}")
                
            except Exception as e:
                workflow.logger.error(f"Optimization workflow failed: {e}")
            
            # Wait for next run
            await asyncio.sleep(settings.evaluation_frequency_seconds)
