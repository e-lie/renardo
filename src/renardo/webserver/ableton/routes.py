from fastapi import APIRouter, HTTPException
from .models import (
    AbletonStatusResponse,
    AbletonActionResponse,
    AbletonStartupSettingResponse,
    AbletonStartupSettingRequest,
)
from .service import ableton_service

router = APIRouter(prefix="/api/ableton", tags=["ableton"])


@router.get("/status", response_model=AbletonStatusResponse)
async def get_status():
    return AbletonStatusResponse(**ableton_service.get_status())


@router.post("/start", response_model=AbletonActionResponse)
async def start():
    result = ableton_service.start()
    return AbletonActionResponse(**result)


@router.post("/stop", response_model=AbletonActionResponse)
async def stop():
    result = ableton_service.stop()
    return AbletonActionResponse(**result)


@router.post("/restart", response_model=AbletonActionResponse)
async def restart():
    result = ableton_service.restart()
    return AbletonActionResponse(**result)


@router.get("/settings/startup-enabled", response_model=AbletonStartupSettingResponse)
async def get_startup_enabled():
    return AbletonStartupSettingResponse(enabled=ableton_service.is_startup_enabled())


@router.post("/settings/startup-enabled", response_model=AbletonStartupSettingResponse)
async def set_startup_enabled(request: AbletonStartupSettingRequest):
    ok = ableton_service.set_startup_enabled(request.enabled)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to save setting")
    return AbletonStartupSettingResponse(enabled=request.enabled)
