"""Tools for reaside."""

# Import the unified client (with OSC support)
from .reaper_client import ReaperClient

# Import the HTTP-only client for backwards compatibility and initialization
from .reaper_http_client import ReaperClient as ReaperHTTPClient, ReaperHTTPError, ReaperAPIError, ReaperNotFoundError

# Import OSC client (with fallback if python-osc not available)
try:
    from .reaper_osc_client import ReaperOSCClient, ReaperOSCError
except ImportError:
    # python-osc not available
    ReaperOSCClient = None
    ReaperOSCError = None

# Import from the reaper_program module
from .reaper_program import start_reaper, stop_reaper, is_reaper_running