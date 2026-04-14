"""Evaluation controller - handles evaluation log requests."""
from typing import List
from models.api_models import EvaluationLogResponse
from service.evaluation_service import EvaluationService


class EvaluationController:
    """Controller for evaluation operations."""
    
    def __init__(self):
        self.evaluation_service = EvaluationService()
    
    async def get_recent_evaluations(self, limit: int) -> List[EvaluationLogResponse]:
        """Get recent evaluation logs."""
        logs = await self.evaluation_service.get_recent_evaluations(limit)
        
        return [
            EvaluationLogResponse(
                id=str(log.id),
                prompt_id=log.prompt_id,
                input_query=log.input_query,
                output_response=log.output_response,
                judge_feedback=log.judge_feedback,
                judge_score=log.judge_score,
                execution_time_ms=log.execution_time_ms,
                created_at=log.created_at
            )
            for log in logs
        ]
    
    async def get_evaluations_for_prompt(self, prompt_id: str, limit: int) -> List[EvaluationLogResponse]:
        """Get evaluation logs for a specific prompt."""
        logs = await self.evaluation_service.get_evaluations_for_prompt(prompt_id, limit)
        
        return [
            EvaluationLogResponse(
                id=str(log.id),
                prompt_id=log.prompt_id,
                input_query=log.input_query,
                output_response=log.output_response,
                judge_feedback=log.judge_feedback,
                judge_score=log.judge_score,
                execution_time_ms=log.execution_time_ms,
                created_at=log.created_at
            )
            for log in logs
        ]
