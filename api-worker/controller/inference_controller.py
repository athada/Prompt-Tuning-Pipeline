"""Inference controller - handles inference requests."""
import time
from models.api_models import InferenceRequest, InferenceResponse
from models.database_models import PromptType
from service.prompt_service import PromptService
from service.llm_service import LLMService
from service.evaluation_service import EvaluationService


class InferenceController:
    """Controller for inference operations."""
    
    def __init__(self):
        self.prompt_service = PromptService()
        self.llm_service = LLMService()
        self.evaluation_service = EvaluationService()
    
    async def run_inference(self, request: InferenceRequest) -> InferenceResponse:
        """Run inference using active or experimental prompts."""
        start_time = time.time()
        
        # Get the prompt to use
        if request.prompt_id:
            if request.use_experimental:
                prompt = await self.prompt_service.get_experimental_prompt_by_id(request.prompt_id)
            else:
                prompt = await self.prompt_service.get_active_prompt_by_id(request.prompt_id)
        else:
            if request.use_experimental:
                prompts = await self.prompt_service.get_top_experimental_prompts(limit=1)
                prompt = prompts[0] if prompts else None
            else:
                prompt = await self.prompt_service.get_active_prompt(PromptType.SYSTEM)
        
        if not prompt:
            raise ValueError("No suitable prompt found")
        
        # Run inference
        inference_output = await self.llm_service.run_inference(
            query=request.query,
            system_prompt=prompt.prompt_text
        )
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        # Evaluate the response
        judge_result = await self.evaluation_service.evaluate_and_log(
            query=request.query,
            response=inference_output.response,
            prompt_text=prompt.prompt_text,
            prompt_id=str(prompt.id),
            execution_time_ms=execution_time_ms
        )
        
        # Update prompt score if it's active
        if not request.use_experimental:
            await self.prompt_service.update_active_prompt_score(
                prompt_id=str(prompt.id),
                score=judge_result["score"]
            )
        
        return InferenceResponse(
            response=inference_output.response,
            prompt_id=str(prompt.id),
            prompt_text=prompt.prompt_text,
            execution_time_ms=execution_time_ms,
            metadata={
                "confidence": inference_output.confidence,
                "reasoning": inference_output.reasoning,
                "judge_score": judge_result["score"]
            }
        )
