"""FastAPI application setup."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from service.database_service import db_service
from service.temporal_service import temporal_service
from api.routes import inference_routes, prompt_routes, evaluation_routes, optimization_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    logger.info("Starting Prompt Tuning Pipeline...")
    
    # Connect to database
    await db_service.connect()
    logger.info("Connected to MongoDB")
    
    # Start Temporal worker
    await temporal_service.start_worker()
    logger.info("Temporal worker started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await temporal_service.stop_worker()
    await db_service.disconnect()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Prompt Tuning Pipeline API",
        description="Automated LLM prompt optimization using LLM-as-a-Judge",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routes
    app.include_router(inference_routes.router, prefix="/api", tags=["inference"])
    app.include_router(prompt_routes.router, prefix="/api", tags=["prompts"])
    app.include_router(evaluation_routes.router, prefix="/api", tags=["evaluations"])
    app.include_router(optimization_routes.router, prefix="/api", tags=["optimization"])
    
    return app


app = create_app()
