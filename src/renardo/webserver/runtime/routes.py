from fastapi import APIRouter
from .models import RuntimeStatusResponse, RuntimeActionResponse
from .service import runtime_service

router = APIRouter(prefix="/api/runtime", tags=["runtime"])


@router.get("/status", response_model=RuntimeStatusResponse)
async def get_runtime_status():
    """Get current Renardo runtime subprocess status."""
    return RuntimeStatusResponse(**runtime_service.get_status())


@router.post("/start", response_model=RuntimeActionResponse)
async def start_runtime():
    """Start the Renardo runtime as a separate subprocess."""
    result = runtime_service.start()
    return RuntimeActionResponse(**result)


@router.post("/stop", response_model=RuntimeActionResponse)
async def stop_runtime():
    """Stop the Renardo runtime subprocess."""
    result = runtime_service.stop()
    return RuntimeActionResponse(**result)


@router.post("/restart", response_model=RuntimeActionResponse)
async def restart_runtime():
    """Restart the Renardo runtime subprocess."""
    result = runtime_service.restart()
    return RuntimeActionResponse(**result)
