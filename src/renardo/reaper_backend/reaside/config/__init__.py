"""Configuration module for reaside."""

from .config import (
    WEB_INTERFACE_PORT,
    configure_reaper_lua as configure_reaper
)
from .resource_path import get_resource_path