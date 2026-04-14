"""Evaluation service - handles evaluation logic."""
from typing import List, Optional, Dict, Any
from bson import ObjectId

from models.database_models import EvaluationLogModel
from service.database_service import db_service
from service.llm_service import LLMService


class EvaluationService:
    """Service for evaluation operations."""
    
    def __init__(self):
        self.llm_service = LLMService()
    
    @property
    def db(self):
        return db_service.get_database()
    
    async def evaluate_and_log(
        self,
        query: str,
        response: str,
        prompt_text: str,
        prompt_id: str,
        execution_time_ms: float
    ) -> Dict[str, Any]:
        """Evaluate a response and log it to the database."""
        judge_output = await self.llm_service.judge_response(
            query=query,
            response=response,
            prompt_used=prompt_text
        )
        
        # Create evaluation log
        log = EvaluationLogModel(
            prompt_id=prompt_id,
            prompt_text=prompt_text,
            input_query=query,
            output_response=response,
            judge_feedback=judge_output.feedback,
            judge_score=judge_output.score,
            execution_time_ms=execution_time_ms,
            metadata={
                "strengths": judge_output.strengths,
                "weaknesses": judge_output.weaknesses,
                "recommendations": judge_output.recommendations
            }
        )
        
        await self.create_evaluation_log(log)
        
        return {
            "score": judge_output.score,
            "feedback": judge_output.feedback,
            "strengths": judge_output.strengths,
            "weaknesses": judge_output.weaknesses,
            "recommendations": judge_output.recommendations
        }
    
    async def create_evaluation_log(self, log: EvaluationLogModel) -> str:
        """Create a new evaluation log."""
        result = await self.db.evaluation_logs.insert_one(
            log.model_dump(by_alias=True, exclude={"id"})
        )
        return str(result.inserted_id)
    
    async def get_recent_evaluations(self, limit: int = 100) -> List[EvaluationLogModel]:
        """Get recent evaluation logs."""
        cursor = self.db.evaluation_logs.find({}).sort("created_at", -1).limit(limit)
        logs = []
        async for doc in cursor:
            logs.append(EvaluationLogModel(**doc))
        return logs
    
    async def get_evaluations_for_prompt(self, prompt_id: str, limit: int = 50) -> List[EvaluationLogModel]:
        """Get evaluation logs for a specific prompt."""
        cursor = self.db.evaluation_logs.find(
            {"prompt_id": prompt_id}
        ).sort("created_at", -1).limit(limit)
        logs = []
        async for doc in cursor:
            logs.append(EvaluationLogModel(**doc))
        return logs
    
    async def get_low_score_evaluations(self, threshold: float, limit: int = 50) -> List[EvaluationLogModel]:
        """Get evaluation logs with scores below threshold."""
        cursor = self.db.evaluation_logs.find(
            {"judge_score": {"$lt": threshold}}
        ).sort("created_at", -1).limit(limit)
        logs = []
        async for doc in cursor:
            logs.append(EvaluationLogModel(**doc))
        return logs
