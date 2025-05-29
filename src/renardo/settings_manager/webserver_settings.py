"""
Webserver settings module for Renardo.

This module defines settings related to the Flask web server
and the HTTP/WebSocket API.
"""

from .settings_manager import settings

# Define default public settings
webserver_public_defaults = {
    "webserver": {
        "FLASK_DEBUG": False,  # Set to False by default for production
        "HOST": "0.0.0.0",  # Listen on all interfaces by default
        "PORT": 12345,  # Default port
        "AUTOCLOSE_WEBCLIENT": True,  # Auto-close browser tabs when webserver stops
    }
}

# Define default internal settings (not visible/changeable by users)
webserver_internal_defaults = {
    "webserver": {
        "STATIC_FOLDER_PATH": "",  # Will be dynamically resolved
        "WEBSOCKET_ROUTE": "/ws",
        "PING_INTERVAL": 25,  # WebSocket ping interval in seconds
    }
}

# Register the defaults with the settings manager
settings.set_defaults_from_dict(webserver_public_defaults)
settings.set_defaults_from_dict(webserver_internal_defaults, internal=True)

# Save the settings
settings.save_to_file()
