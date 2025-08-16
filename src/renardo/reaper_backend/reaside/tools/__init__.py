"""Tools for reaside."""

# Import the unified client (with OSC support)
from .reaper_client import ReaperClient

# Import the HTTP-only client for backwards compatibility and initialization
from .reaper_http_client import ReaperClient as ReaperHTTPClient, ReaperHTTPError, ReaperAPIError, ReaperNotFoundError


# Import from the reaper_program module
from .reaper_program import start_reaper, stop_reaper, is_reaper_running