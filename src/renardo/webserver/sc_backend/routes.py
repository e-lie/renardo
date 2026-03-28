from fastapi import APIRouter, HTTPException
from .models import (
    StartBackendRequest, StartBackendResponse,
    StopBackendResponse, StatusResponse,
    AudioDevicesResponse, LaunchIDEResponse,
    AudioDeviceSettingRequest, AudioDeviceSettingResponse,
    ChannelsSettingRequest, ChannelsSettingResponse,
    ReconfigureResponse
)

router = APIRouter(prefix="/api/sc-backend", tags=["sc-backend"])

# Service instance (initialized by init_sc_service)
sc_service = None


def init_sc_service(websocket_manager):
    """Initialize SC backend service with WebSocket manager."""
    global sc_service
    from renardo.sc_backend.sc_backend_service import SCBackendService
    sc_service = SCBackendService(websocket_manager)


@router.post("/start", response_model=StartBackendResponse)
async def start_backend(request: StartBackendRequest):
    """Start SuperCollider backend."""
    if sc_service is None:
        raise HTTPException(status_code=500, detail="SC service not initialized")

    try:
        result = await sc_service.start_backend(request.audio_output_index)
        return StartBackendResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting backend: {str(e)}")


@router.post("/stop", response_model=StopBackendResponse)
async def stop_backend():
    """Stop SuperCollider backend."""
    if sc_service is None:
        raise HTTPException(status_code=500, detail="SC service not initialized")

    try:
        result = await sc_service.stop_backend()
        return StopBackendResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping backend: {str(e)}")


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get current SC backend status."""
    if sc_service is None:
        raise HTTPException(status_code=500, detail="SC service not initialized")

    try:
        result = sc_service.get_status()
        return StatusResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")


@router.get("/audio-devices", response_model=AudioDevicesResponse)
async def get_audio_devices():
    """Get available audio devices (non-Linux only)."""
    if sc_service is None:
        raise HTTPException(status_code=500, detail="SC service not initialized")

    try:
        result = sc_service.get_audio_devices()
        return AudioDevicesResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting audio devices: {str(e)}")


@router.post("/launch-ide", response_model=LaunchIDEResponse)
async def launch_ide():
    """Launch SuperCollider IDE."""
    if sc_service is None:
        raise HTTPException(status_code=500, detail="SC service not initialized")

    try:
        result = sc_service.launch_ide()
        return LaunchIDEResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error launching IDE: {str(e)}")


@router.get("/settings/audio-device", response_model=AudioDeviceSettingResponse)
async def get_audio_device_setting():
    """Get current audio device setting."""
    if sc_service is None:
        raise HTTPException(status_code=500, detail="SC service not initialized")

    try:
        index = sc_service.get_audio_device_setting()
        return AudioDeviceSettingResponse(audio_output_index=index)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting setting: {str(e)}")


@router.post("/settings/audio-device", response_model=AudioDeviceSettingResponse)
async def set_audio_device_setting(request: AudioDeviceSettingRequest):
    """Set audio device setting."""
    if sc_service is None:
        raise HTTPException(status_code=500, detail="SC service not initialized")

    try:
        success = sc_service.set_audio_device_setting(request.audio_output_index)
        if success:
            return AudioDeviceSettingResponse(audio_output_index=request.audio_output_index)
        else:
            raise HTTPException(status_code=500, detail="Failed to set audio device")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting device: {str(e)}")


@router.get("/settings/channels", response_model=ChannelsSettingResponse)
async def get_channels_setting():
    """Get current channels settings."""
    if sc_service is None:
        raise HTTPException(status_code=500, detail="SC service not initialized")

    try:
        channels = sc_service.get_channels_settings()
        return ChannelsSettingResponse(**channels)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting channels: {str(e)}")


@router.post("/settings/channels", response_model=ChannelsSettingResponse)
async def set_channels_setting(request: ChannelsSettingRequest):
    """Set channels settings and regenerate SC files."""
    if sc_service is None:
        raise HTTPException(status_code=500, detail="SC service not initialized")

    try:
        success = await sc_service.set_channels_settings(
            request.num_output_channels,
            request.num_input_channels
        )
        if success:
            return ChannelsSettingResponse(
                num_output_channels=request.num_output_channels,
                num_input_channels=request.num_input_channels
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to set channels")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting channels: {str(e)}")


@router.post("/reconfigure", response_model=ReconfigureResponse)
async def reconfigure_backend():
    """Regenerate SC files, stop and restart backend with new configuration."""
    if sc_service is None:
        raise HTTPException(status_code=500, detail="SC service not initialized")

    try:
        result = await sc_service.reconfigure_backend()
        return ReconfigureResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reconfiguring: {str(e)}")
