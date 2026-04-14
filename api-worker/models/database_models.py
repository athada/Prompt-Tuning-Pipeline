"""Database models and schemas for the prompt tuning system."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class PromptStatus(str, Enum):
    """Status of a prompt in the system."""
    ACTIVE = "active"
    EXPERIMENTAL = "experimental"
    ARCHIVED = "archived"
    FAILED = "failed"


class PromptType(str, Enum):
    """Type of prompt based on its purpose."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


# ============================================================================
# Database Models (for MongoDB documents)
# ============================================================================

class ActivePromptModel(BaseModel):
    """Schema for active_prompts collection."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    prompt_text: str
    prompt_type: PromptType
    agent_name: str
    parent_chain: List[str] = Field(default_factory=list)
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    performance_score: float = 0.0
    usage_count: int = 0
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ExperimentalPromptModel(BaseModel):
    """Schema for experimental_prompts collection."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    prompt_text: str
    prompt_type: PromptType
    agent_name: str
    parent_prompt_id: Optional[str] = None
    parent_chain: List[str] = Field(default_factory=list)
    generation_rationale: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tested_at: Optional[datetime] = None
    test_score: Optional[float] = None
    status: PromptStatus = PromptStatus.EXPERIMENTAL
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class EvaluationLogModel(BaseModel):
    """Schema for evaluation_logs collection."""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    prompt_id: str
    prompt_text: str
    input_query: str
    output_response: str
    judge_feedback: str
    judge_score: float
    execution_time_ms: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ============================================================================
# API Request/Response Models
# ============================================================================

class InferenceRequest(BaseModel):
    """Request model for running inference."""
    query: str
    use_experimental: bool = False
    prompt_id: Optional[str] = None


class InferenceResponse(BaseModel):
    """Response model for inference results."""
    response: str
    prompt_id: str
    prompt_text: str
    execution_time_ms: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PromptResponse(BaseModel):
    """Response model for prompt data."""
    id: str
    prompt_text: str
    prompt_type: str
    status: str
    created_at: datetime
    performance_score: Optional[float] = None
    test_score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class OptimizationTriggerRequest(BaseModel):
    """Request to manually trigger the optimization workflow."""
    batch_size: Optional[int] = None
    force_regenerate: bool = False


class OptimizationTriggerResponse(BaseModel):
    """Response from triggering optimization."""
    workflow_id: str
    run_id: str
    message: str


class PromotePromptRequest(BaseModel):
    """Request to promote an experimental prompt to active."""
    experimental_prompt_id: str
    archive_old_prompt: bool = True


class EvaluationLogResponse(BaseModel):
    """Response model for evaluation logs."""
    id: str
    prompt_id: str
    input_query: str
    output_response: str
    judge_feedback: str
    judge_score: float
    execution_time_ms: float
    created_at: datetime
