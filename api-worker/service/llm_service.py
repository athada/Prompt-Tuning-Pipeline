"""LLM service - handles all LLM interactions via PydanticAI."""
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel

from config import settings


# ============================================================================
# Structured Output Schemas
# ============================================================================

class GeneratorOutput(BaseModel):
    """Structured output from the Generator Agent."""
    improved_prompt: str = Field(description="The new, improved prompt text")
    rationale: str = Field(description="Explanation of why this prompt is better")
    key_changes: List[str] = Field(description="List of key changes made to the prompt")
    expected_improvement: str = Field(description="What improvement is expected from this new prompt")


class JudgeOutput(BaseModel):
    """Structured output from the Judge Agent."""
    score: float = Field(ge=0.0, le=10.0, description="Quality score from 0-10")
    feedback: str = Field(description="Detailed critique and feedback")
    strengths: List[str] = Field(description="What the response did well")
    weaknesses: List[str] = Field(description="What needs improvement")
    recommendations: List[str] = Field(description="Specific recommendations for improvement")


class InferenceOutput(BaseModel):
    """Structured output from the Inference Agent."""
    response: str = Field(description="The generated response to the user query")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in the response")
    reasoning: str = Field(default=None, description="Brief explanation of the reasoning")


# ============================================================================
# LLM Service
# ============================================================================

class LLMService:
    """Service for LLM interactions using PydanticAI."""
    
    def __init__(self):
        """Initialize LLM service with Ollama model."""
        self.ollama_model = OllamaModel(
            model_name=settings.ollama_model,
            base_url=settings.ollama_base_url
        )
        
        # Generator Agent
        self.generator_agent = Agent(
            model=self.ollama_model,
            result_type=GeneratorOutput,
            system_prompt="""You are an expert prompt engineer specializing in optimizing LLM prompts.

Your task is to analyze feedback on a prompt's performance and generate an improved version.

When creating improved prompts:
1. Address specific weaknesses identified in the feedback
2. Maintain the core purpose and intent of the original prompt
3. Add clarity, structure, and specificity where needed
4. Remove ambiguity and potential sources of confusion
5. Incorporate best practices for prompt engineering
6. Consider edge cases and failure modes

Focus on actionable improvements that will directly address the issues identified."""
        )
        
        # Judge Agent
        self.judge_agent = Agent(
            model=self.ollama_model,
            result_type=JudgeOutput,
            system_prompt="""You are an expert AI evaluator responsible for assessing the quality of LLM responses.

Your task is to provide objective, detailed evaluations of responses based on:
1. Accuracy and correctness
2. Relevance to the user's query
3. Completeness of the answer
4. Clarity and coherence
5. Helpfulness and actionability
6. Appropriate level of detail

Provide scores on a scale of 0-10 where:
- 0-3: Poor quality, major issues
- 4-6: Acceptable but with notable problems
- 7-8: Good quality with minor issues
- 9-10: Excellent quality, minimal or no issues

Be critical but fair. Focus on providing actionable feedback."""
        )
    
    async def generate_improved_prompt(
        self,
        original_prompt: str,
        agent_name: str,
        feedback: str,
        low_score_examples: List[Dict[str, Any]]
    ) -> GeneratorOutput:
        """Generate an improved prompt based on feedback."""
        user_message = f"""Agent: {agent_name}

Original Prompt:
{original_prompt}

Feedback from Recent Evaluations:
{feedback}

Low-Scoring Examples:
"""
        for i, example in enumerate(low_score_examples[:3], 1):
            user_message += f"\nExample {i}:\n"
            user_message += f"Query: {example.get('query', 'N/A')}\n"
            user_message += f"Response: {example.get('response', 'N/A')[:200]}...\n"
            user_message += f"Score: {example.get('score', 'N/A')}\n"
            user_message += f"Issues: {example.get('feedback', 'N/A')}\n"
        
        user_message += "\n\nGenerate an improved version of the original prompt that addresses these issues."
        
        result = await self.generator_agent.run(user_message)
        return result.data
    
    async def judge_response(
        self,
        query: str,
        response: str,
        prompt_used: str
    ) -> JudgeOutput:
        """Evaluate the quality of a response."""
        user_message = f"""Evaluate the following interaction:

User Query: {query}

AI Response: {response}

Prompt Used: {prompt_used}

Provide a detailed evaluation with a score from 0-10."""
        
        result = await self.judge_agent.run(user_message)
        return result.data
    
    async def run_inference(
        self,
        query: str,
        system_prompt: str
    ) -> InferenceOutput:
        """Run inference with a specific prompt."""
        temp_agent = Agent(
            model=self.ollama_model,
            result_type=InferenceOutput,
            system_prompt=system_prompt
        )
        
        result = await temp_agent.run(query)
        return result.data
