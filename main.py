"""
Main entry point for the SheetAgent API server.

Starts the FastAPI server via Uvicorn with hot-reload enabled for development.
Logging is configured before the server launches.
"""

import logging

import uvicorn

from app.core.config import get_settings
from app.core.logging_config import configure_logging

configure_logging(force=True)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    settings = get_settings()

    logger.info("Starting SheetAgent API on %s:%s", settings.HOST, settings.PORT)
    uvicorn.run(
        "app.app:create_app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        factory=True,
        reload_dirs=["app"],
        log_level="info",
        log_config=None,
    )
