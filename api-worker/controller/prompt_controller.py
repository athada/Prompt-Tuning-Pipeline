"""Prompt controller - handles prompt management."""
from typing import List
from models.api_models import PromptResponse, PromotePromptRequest
from models.database_models import PromptType
from service.prompt_service import PromptService


class PromptController:
    """Controller for prompt operations."""
    
    def __init__(self):
        self.prompt_service = PromptService()
    
    async def get_active_prompts(self) -> List[PromptResponse]:
        """Get all active prompts."""
        prompts = await self.prompt_service.get_all_active_prompts()
        
        return [
            PromptResponse(
                id=str(p.id),
                prompt_text=p.prompt_text,
                prompt_type=p.prompt_type,
                status="active",
                created_at=p.created_at,
                performance_score=p.performance_score,
                metadata={
                    "version": p.version,
                    "usage_count": p.usage_count,
                    "agent_name": p.agent_name,
                    "parent_chain": p.parent_chain,
                    **p.metadata
                }
            )
            for p in prompts
        ]
    
    async def get_experimental_prompts(self, limit: int) -> List[PromptResponse]:
        """Get all experimental prompts."""
        prompts = await self.prompt_service.get_all_experimental_prompts(limit=limit)
        
        return [
            PromptResponse(
                id=str(p.id),
                prompt_text=p.prompt_text,
                prompt_type=p.prompt_type,
                status=p.status,
                created_at=p.created_at,
                test_score=p.test_score,
                metadata={
                    "parent_prompt_id": p.parent_prompt_id,
                    "generation_rationale": p.generation_rationale,
                    "tested_at": p.tested_at.isoformat() if p.tested_at else None,
                    "agent_name": p.agent_name,
                    "parent_chain": p.parent_chain,
                    **p.metadata
                }
            )
            for p in prompts
        ]
    
    async def get_top_experimental_prompts(self, limit: int) -> List[PromptResponse]:
        """Get top-performing experimental prompts."""
        prompts = await self.prompt_service.get_top_experimental_prompts(limit=limit)
        
        return [
            PromptResponse(
                id=str(p.id),
                prompt_text=p.prompt_text,
                prompt_type=p.prompt_type,
                status=p.status,
                created_at=p.created_at,
                test_score=p.test_score,
                metadata={
                    "parent_prompt_id": p.parent_prompt_id,
                    "generation_rationale": p.generation_rationale,
                    "agent_name": p.agent_name,
                    "parent_chain": p.parent_chain,
                    **p.metadata
                }
            )
            for p in prompts
        ]
    
    async def promote_prompt(self, request: PromotePromptRequest) -> dict:
        """Promote an experimental prompt to active status."""
        # Archive old active prompt if requested
        if request.archive_old_prompt:
            old_active = await self.prompt_service.get_active_prompt(PromptType.SYSTEM)
            if old_active:
                await self.prompt_service.archive_active_prompt(str(old_active.id))
        
        # Promote experimental to active
        new_active_id = await self.prompt_service.promote_experimental_to_active(
            request.experimental_prompt_id
        )
        
        return {
            "status": "success",
            "new_active_prompt_id": new_active_id,
            "message": "Experimental prompt promoted to active"
        }
