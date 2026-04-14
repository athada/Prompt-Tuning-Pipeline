"""Database initialization script - seeds base prompts with agent names and tracking."""
import asyncio
from datetime import datetime

from service.database_service import db_service
from models.database_models import ActivePromptModel, PromptType
from prompts.base_prompts import get_base_prompts


async def seed_base_prompts():
    """Seed the database with base prompts from configuration."""
    await db_service.connect()
    
    base_prompts = get_base_prompts()
    
    print(f"Seeding {len(base_prompts)} base prompts...")
    
    for base_prompt in base_prompts:
        # Check if prompt with this agent_name already exists
        existing = await db_service.db.active_prompts.find_one(
            {"agent_name": base_prompt.agent_name}
        )
        
        if existing:
            print(f"  ✓ Agent '{base_prompt.agent_name}' already exists, skipping")
            continue
        
        # Create active prompt from base prompt
        active_prompt = ActivePromptModel(
            agent_name=base_prompt.agent_name,
            prompt_text=base_prompt.prompt_text,
            prompt_type=PromptType(base_prompt.prompt_type),
            parent_chain=[],  # Root prompts have empty chain
            version=1,
            performance_score=base_prompt.performance_score,
            usage_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={
                "description": base_prompt.description,
                "is_base_prompt": True,
                "created_by": "seed_script"
            }
        )
        
        result = await db_service.db.active_prompts.insert_one(
            active_prompt.model_dump(by_alias=True, exclude={"id"})
        )
        
        print(f"  ✓ Created '{base_prompt.agent_name}' (ID: {result.inserted_id})")
    
    await db_service.disconnect()
    print("\nDatabase seeded successfully!")
    print(f"\nTotal agents seeded: {len(base_prompts)}")
    print("\nAgent names:")
    for bp in base_prompts:
        print(f"  - {bp.agent_name}")


if __name__ == "__main__":
    asyncio.run(seed_base_prompts())
