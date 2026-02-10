"""Health and readiness probe endpoints."""

from fastapi import APIRouter, HTTPException, Request, status

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Liveness probe — confirms the process is running."""
    return {"status": "ok"}


@router.get("/ready", tags=["Health"])
async def readiness_check(request: Request) -> dict[str, str]:
    """Readiness probe — confirms the application has finished initialisation."""
    if not hasattr(request.app.state, "ready") or not request.app.state.ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Application is not ready yet",
        )
    return {"status": "ready"}
