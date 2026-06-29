from pydantic import BaseModel


class AbletonStatusResponse(BaseModel):
    status: str
    message: str


class AbletonActionResponse(BaseModel):
    success: bool
    status: str
    message: str


class AbletonStartupSettingResponse(BaseModel):
    enabled: bool


class AbletonStartupSettingRequest(BaseModel):
    enabled: bool
