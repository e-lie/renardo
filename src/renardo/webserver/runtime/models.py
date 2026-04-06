from pydantic import BaseModel
from typing import Optional


class RuntimeStatusResponse(BaseModel):
    running: bool
    status: str
    pid: Optional[int] = None


class RuntimeActionResponse(BaseModel):
    success: bool
    message: str
    running: bool
    status: str
    pid: Optional[int] = None
