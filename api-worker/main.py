"""Main application entry point."""
import uvicorn
import logging

from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    logger.info(f"Starting API server on {settings.api_host}:{settings.api_port}")
    logger.info(f"Ollama base URL: {settings.ollama_base_url}")
    logger.info(f"MongoDB URI: {settings.mongodb_uri}")
    
    uvicorn.run(
        "api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
