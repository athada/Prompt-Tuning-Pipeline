"""Database service - manages MongoDB connection."""
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import DESCENDING, ASCENDING

from config import settings

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database connection management."""
    
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db: AsyncIOMotorDatabase = None
    
    async def connect(self):
        """Connect to MongoDB and create indexes."""
        self.client = AsyncIOMotorClient(settings.mongodb_uri)
        self.db = self.client[settings.mongodb_database]
        
        logger.info(f"Connected to MongoDB: {settings.mongodb_uri}")
        
        # Create indexes
        await self._create_indexes()
        logger.info("Database indexes created")
    
    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """Create database indexes for performance."""
        # Active prompts indexes
        await self.db.active_prompts.create_index([("agent_name", ASCENDING)])
        await self.db.active_prompts.create_index([("performance_score", DESCENDING)])
        await self.db.active_prompts.create_index([("created_at", DESCENDING)])
        
        # Experimental prompts indexes
        await self.db.experimental_prompts.create_index([("agent_name", ASCENDING)])
        await self.db.experimental_prompts.create_index([("status", ASCENDING)])
        await self.db.experimental_prompts.create_index([("test_score", DESCENDING)])
        await self.db.experimental_prompts.create_index([("created_at", DESCENDING)])
        await self.db.experimental_prompts.create_index([("parent_prompt_id", ASCENDING)])
        
        # Evaluation logs indexes
        await self.db.evaluation_logs.create_index([("prompt_id", ASCENDING)])
        await self.db.evaluation_logs.create_index([("judge_score", DESCENDING)])
        await self.db.evaluation_logs.create_index([("created_at", DESCENDING)])
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """Get the database instance."""
        if not self.db:
            raise RuntimeError("Database not connected")
        return self.db


# Global database service instance
db_service = DatabaseService()
