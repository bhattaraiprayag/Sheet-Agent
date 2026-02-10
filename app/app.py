"""
FastAPI application factory module.

Provides the factory function to create and configure the SheetAgent
FastAPI application with middleware, exception handlers, and routers.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.endpoints import health, opos
from app.core.logging_config import configure_logging

logger = logging.getLogger(__name__)
API_PREFIX = "/api/v1"


def create_app() -> FastAPI:
    # Lifespan Events
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        configure_logging(force=True)
        # Force reconfigure logging to ensure it works with uvicorn
        logger.info("🚀 Starting FastAPI app...")
        # Initialize environment variables if not already done
        app.state.ready = True
        yield
        logger.info("👋 Shutting down FastAPI app...")
        app.state.ready = False

    # Exception Handler
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(exc)},
        )

    app = FastAPI(
        title="SheetAgent",
        description="AI-powered A/R aging report generation API.",
        version="0.1.0",
        lifespan=lifespan,
        openapi_tags=[
            {"name": "Health", "description": "Health and readiness probes"},
            {"name": "Open Post Analysis", "description": "A/R aging report generation"},
        ],
    )

    app.add_exception_handler(Exception, global_exception_handler)

    app.include_router(health.router, prefix=API_PREFIX)
    app.include_router(opos.router, prefix="/opos", tags=["Open Post Analysis"])
    return app
