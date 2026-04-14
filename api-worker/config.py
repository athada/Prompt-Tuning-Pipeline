"""Configuration management for the API/Worker service."""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False
    
    # Temporal Settings
    temporal_host: str = "temporal:7233"
    temporal_namespace: str = "default"
    temporal_task_queue: str = "prompt-tuning-queue"
    
    # Database Settings
    mongodb_uri: str = "mongodb://mongodb:27017"
    mongodb_database: str = "prompt_tuning"
    
    # Ollama Settings
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_model: str = "gemma2"
    
    # LLM Settings
    generator_model: str = "gemma2"
    judge_model: str = "gemma2"
    temperature: float = 0.7
    max_tokens: int = 2000
    
    # Optimization Settings
    batch_size: int = 10
    score_threshold: float = 7.0
    evaluation_frequency_seconds: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
