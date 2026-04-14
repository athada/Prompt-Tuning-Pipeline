"""Temporal workflow activities - business logic for workflows."""
from datetime import datetime
from typing import List, Dict, Any
from temporalio import activity

from config import settings
from models.database_models import PromptType, ExperimentalPromptModel
from service.evaluation_service import EvaluationService
from service.prompt_service import PromptService
from service.llm_service import LLMService


# Initialize services
evaluation_service = EvaluationService()
prompt_service = PromptService()
llm_service = LLMService()


@activity.defn
async def fetch_recent_low_score_evaluations(batch_size: int) -> List[Dict[str, Any]]:
    """Fetch recent evaluations with low scores."""
    logs = await evaluation_service.get_low_score_evaluations(
        threshold=settings.score_threshold,
        limit=batch_size
    )
    
    return [
        {
            "id": str(log.id),
            "prompt_id": log.prompt_id,
            "prompt_text": log.prompt_text,
            "query": log.input_query,
            "response": log.output_response,
            "feedback": log.judge_feedback,
            "score": log.judge_score,
            "execution_time_ms": log.execution_time_ms
        }
        for log in logs
    ]


@activity.defn
async def evaluate_prompt_performance(
    query: str,
    response: str,
    prompt_text: str,
    prompt_id: str,
    execution_time_ms: float
) -> Dict[str, Any]:
    """Evaluate a response using the Judge Agent."""
    return await evaluation_service.evaluate_and_log(
        query=query,
        response=response,
        prompt_text=prompt_text,
        prompt_id=prompt_id,
        execution_time_ms=execution_time_ms
    )


@activity.defn
async def generate_improved_prompt(
    original_prompt_id: str,
    original_prompt_text: str,
    agent_name: str,
    parent_chain: List[str],
    low_score_examples: List[Dict[str, Any]]
) -> str:
    """Generate an improved prompt using the Generator Agent."""
    # Aggregate feedback
    aggregated_feedback = "\n\n".join([
        f"Score {ex['score']}: {ex['feedback']}" 
        for ex in low_score_examples[:5]
    ])
    
    generator_output = await llm_service.generate_improved_prompt(
        original_prompt=original_prompt_text,
        agent_name=agent_name,
        feedback=aggregated_feedback,
        low_score_examples=low_score_examples
    )
    
    # Build parent chain for experimental prompt
    new_parent_chain = parent_chain.copy()
    new_parent_chain.append(original_prompt_id)
    
    # Create experimental prompt
    exp_prompt = ExperimentalPromptModel(
        prompt_text=generator_output.improved_prompt,
        prompt_type=PromptType.SYSTEM,
        agent_name=agent_name,
        parent_prompt_id=original_prompt_id,
        parent_chain=new_parent_chain,
        generation_rationale=generator_output.rationale,
        created_at=datetime.utcnow(),
        metadata={
            "key_changes": generator_output.key_changes,
            "expected_improvement": generator_output.expected_improvement
        }
    )
    
    exp_id = await prompt_service.create_experimental_prompt(exp_prompt)
    return exp_id


@activity.defn
async def test_experimental_prompt(
    experimental_prompt_id: str,
    test_queries: List[str]
) -> Dict[str, Any]:
    """Test an experimental prompt with sample queries."""
    exp_prompt = await prompt_service.get_experimental_prompt_by_id(experimental_prompt_id)
    if not exp_prompt:
        raise ValueError(f"Experimental prompt {experimental_prompt_id} not found")
    
    total_score = 0.0
    evaluations = []
    
    for query in test_queries:
        # Run inference
        inference_output = await llm_service.run_inference(
            query=query,
            system_prompt=exp_prompt.prompt_text
        )
        
        # Evaluate
        judge_output = await llm_service.judge_response(
            query=query,
            response=inference_output.response,
            prompt_used=exp_prompt.prompt_text
        )
        
        total_score += judge_output.score
        evaluations.append({
            "query": query,
            "score": judge_output.score,
            "feedback": judge_output.feedback
        })
    
    avg_score = total_score / len(test_queries)
    
    # Update experimental prompt with test results
    await prompt_service.update_experimental_prompt_test_result(
        prompt_id=experimental_prompt_id,
        test_score=avg_score,
        metadata={"test_evaluations": evaluations}
    )
    
    return {
        "experimental_prompt_id": experimental_prompt_id,
        "average_score": avg_score,
        "evaluations": evaluations
    }


@activity.defn
async def get_active_prompt_info() -> Dict[str, Any]:
    """Get current active prompt information."""
    active_prompt = await prompt_service.get_active_prompt(PromptType.SYSTEM)
    
    if not active_prompt:
        return {"exists": False}
    
    return {
        "exists": True,
        "id": str(active_prompt.id),
        "prompt_text": active_prompt.prompt_text,
        "agent_name": active_prompt.agent_name,
        "parent_chain": active_prompt.parent_chain,
        "performance_score": active_prompt.performance_score,
        "usage_count": active_prompt.usage_count
    }
