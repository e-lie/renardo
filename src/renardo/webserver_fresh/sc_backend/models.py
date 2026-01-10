from pydantic import BaseModel
from typing import Dict, Optional


class StartBackendRequest(BaseModel):
    audio_output_index: int = -1


class StartBackendResponse(BaseModel):
    success: bool
    message: str
    running: bool


class StopBackendResponse(BaseModel):
    success: bool
    message: str
    running: bool


class StatusResponse(BaseModel):
    running: bool
    message: str


class AudioDevicesResponse(BaseModel):
    success: bool
    platform: str
    devices: Optional[Dict[str, Dict[int, str]]] = None
    message: Optional[str] = None


class LaunchIDEResponse(BaseModel):
    success: bool
    message: str


class AudioDeviceSettingRequest(BaseModel):
    audio_output_index: int


class AudioDeviceSettingResponse(BaseModel):
    audio_output_index: int


class ChannelsSettingRequest(BaseModel):
    num_output_channels: int
    num_input_channels: int


class ChannelsSettingResponse(BaseModel):
    num_output_channels: int
    num_input_channels: int


class ReconfigureResponse(BaseModel):
    success: bool
    message: str
    regenerated: bool
    restarted: bool
