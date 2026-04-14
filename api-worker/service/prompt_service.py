"""Prompt service - handles prompt business logic."""
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from models.database_models import ActivePromptModel, ExperimentalPromptModel, PromptType, PromptStatus
from service.database_service import db_service


class PromptService:
    """Service for prompt operations."""
    
    @property
    def db(self):
        return db_service.get_database()
    
    # ========================================================================
    # Active Prompts Operations
    # ========================================================================
    
    async def get_active_prompt(self, prompt_type: PromptType = PromptType.SYSTEM) -> Optional[ActivePromptModel]:
        """Get the best active prompt by type."""
        doc = await self.db.active_prompts.find_one(
            {"prompt_type": prompt_type},
            sort=[("performance_score", -1)]
        )
        if doc:
            return ActivePromptModel(**doc)
        return None
    
    async def get_active_prompt_by_id(self, prompt_id: str) -> Optional[ActivePromptModel]:
        """Get active prompt by ID."""
        doc = await self.db.active_prompts.find_one({"_id": ObjectId(prompt_id)})
        if doc:
            return ActivePromptModel(**doc)
        return None
    
    async def get_active_prompt_by_agent_name(self, agent_name: str) -> Optional[ActivePromptModel]:
        """Get active prompt by agent name."""
        doc = await self.db.active_prompts.find_one(
            {"agent_name": agent_name},
            sort=[("performance_score", -1)]
        )
        if doc:
            return ActivePromptModel(**doc)
        return None
    
    async def get_all_active_prompts(self) -> List[ActivePromptModel]:
        """Get all active prompts."""
        cursor = self.db.active_prompts.find({}).sort("performance_score", -1)
        prompts = []
        async for doc in cursor:
            prompts.append(ActivePromptModel(**doc))
        return prompts
    
    async def create_active_prompt(self, prompt: ActivePromptModel) -> str:
        """Create a new active prompt."""
        result = await self.db.active_prompts.insert_one(
            prompt.model_dump(by_alias=True, exclude={"id"})
        )
        return str(result.inserted_id)
    
    async def update_active_prompt_score(self, prompt_id: str, score: float):
        """Update the performance score of an active prompt."""
        await self.db.active_prompts.update_one(
            {"_id": ObjectId(prompt_id)},
            {
                "$set": {
                    "performance_score": score,
                    "updated_at": datetime.utcnow()
                },
                "$inc": {"usage_count": 1}
            }
        )
    
    async def archive_active_prompt(self, prompt_id: str):
        """Archive an active prompt."""
        await self.db.active_prompts.update_one(
            {"_id": ObjectId(prompt_id)},
            {"$set": {"status": "archived", "updated_at": datetime.utcnow()}}
        )
    
    # ========================================================================
    # Experimental Prompts Operations
    # ========================================================================
    
    async def get_experimental_prompt_by_id(self, prompt_id: str) -> Optional[ExperimentalPromptModel]:
        """Get experimental prompt by ID."""
        doc = await self.db.experimental_prompts.find_one({"_id": ObjectId(prompt_id)})
        if doc:
            return ExperimentalPromptModel(**doc)
        return None
    
    async def get_all_experimental_prompts(self, limit: int = 50) -> List[ExperimentalPromptModel]:
        """Get all experimental prompts."""
        cursor = self.db.experimental_prompts.find(
            {"status": PromptStatus.EXPERIMENTAL}
        ).sort("created_at", -1).limit(limit)
        prompts = []
        async for doc in cursor:
            prompts.append(ExperimentalPromptModel(**doc))
        return prompts
    
    async def get_top_experimental_prompts(self, limit: int = 10) -> List[ExperimentalPromptModel]:
        """Get top experimental prompts by test score."""
        cursor = self.db.experimental_prompts.find(
            {
                "status": PromptStatus.EXPERIMENTAL,
                "test_score": {"$ne": None}
            }
        ).sort("test_score", -1).limit(limit)
        prompts = []
        async for doc in cursor:
            prompts.append(ExperimentalPromptModel(**doc))
        return prompts
    
    async def create_experimental_prompt(self, prompt: ExperimentalPromptModel) -> str:
        """Create a new experimental prompt."""
        result = await self.db.experimental_prompts.insert_one(
            prompt.model_dump(by_alias=True, exclude={"id"})
        )
        return str(result.inserted_id)
    
    async def update_experimental_prompt_test_result(
        self,
        prompt_id: str,
        test_score: float,
        metadata: Optional[dict] = None
    ):
        """Update the test score of an experimental prompt."""
        update_data = {
            "test_score": test_score,
            "tested_at": datetime.utcnow()
        }
        if metadata:
            update_data["metadata"] = metadata
        
        await self.db.experimental_prompts.update_one(
            {"_id": ObjectId(prompt_id)},
            {"$set": update_data}
        )
    
    async def promote_experimental_to_active(self, experimental_id: str) -> str:
        """Promote an experimental prompt to active status."""
        exp_prompt = await self.get_experimental_prompt_by_id(experimental_id)
        if not exp_prompt:
            raise ValueError(f"Experimental prompt {experimental_id} not found")
        
        # Build parent chain: parent_chain + parent_id + current_id
        parent_chain = exp_prompt.parent_chain.copy()
        if exp_prompt.parent_prompt_id:
            parent_chain.append(exp_prompt.parent_prompt_id)
        parent_chain.append(experimental_id)
        
        # Create new active prompt
        active_prompt = ActivePromptModel(
            prompt_text=exp_prompt.prompt_text,
            prompt_type=exp_prompt.prompt_type,
            agent_name=exp_prompt.agent_name,
            parent_chain=parent_chain,
            version=1,
            performance_score=exp_prompt.test_score or 0.0,
            metadata={
                "promoted_from": experimental_id,
                "generation_rationale": exp_prompt.generation_rationale
            }
        )
        
        active_id = await self.create_active_prompt(active_prompt)
        
        # Mark experimental as archived
        await self.db.experimental_prompts.update_one(
            {"_id": ObjectId(experimental_id)},
            {"$set": {"status": PromptStatus.ARCHIVED}}
        )
        
        return active_id
