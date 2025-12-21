from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class DirectoryEntry(BaseModel):
    """Entry in a directory (file or folder)"""
    name: str
    path: str
    is_directory: bool
    size: Optional[int] = None
    modified_time: Optional[float] = None
    has_children: bool = False
