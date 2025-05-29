"""
Configuration settings for the Flask application
"""

import os
import logging
import importlib.resources
import sys

# Import settings from settings manager
from renardo.settings_manager import settings

# Server settings
DEBUG = settings.get("webserver.FLASK_DEBUG", False)
HOST = settings.get("webserver.HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", settings.get("webserver.PORT", 12345)))

# Configure Flask logging based on debug mode
if not DEBUG:
    # Set Flask's built-in logger to warning level when debug is disabled
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

# WebSocket settings
WEBSOCKET_ROUTE = settings.get("webserver.WEBSOCKET_ROUTE", "/ws")
PING_INTERVAL = settings.get("webserver.PING_INTERVAL", 25)  # seconds

# Path settings
# When running from source

# Try multiple approaches to find the static files
STATIC_FOLDER_FOUND = False

# Approach 1: Try using importlib.resources (Python 3.9+)
if not STATIC_FOLDER_FOUND and sys.version_info >= (3, 9):
    try:
        static_path = importlib.resources.files("renardo.webserver.static")
        STATIC_FOLDER = str(static_path)
        if os.path.exists(os.path.join(STATIC_FOLDER, "index.html")):
            STATIC_FOLDER_FOUND = True
            if DEBUG:
                print(
                    f"Static folder found using importlib.resources.files: {STATIC_FOLDER}"
                )
    except (ImportError, ModuleNotFoundError, AttributeError, ValueError) as e:
        print(f"importlib.resources.files approach failed: {e}")

# Approach 2: Try using pkg_resources
if not STATIC_FOLDER_FOUND:
    try:
        import pkg_resources

        STATIC_FOLDER = pkg_resources.resource_filename("renardo.webserver.static", "")
        if os.path.exists(os.path.join(STATIC_FOLDER, "index.html")):
            STATIC_FOLDER_FOUND = True
            if DEBUG:
                print(f"Static folder found using pkg_resources: {STATIC_FOLDER}")
    except (ImportError, ModuleNotFoundError, AttributeError, ValueError) as e:
        print(f"pkg_resources approach failed: {e}")

# Approach 3: Try using older importlib.resources API
if not STATIC_FOLDER_FOUND:
    try:
        STATIC_FOLDER = os.path.dirname(
            str(importlib.resources.path("renardo.webserver.static", "index.html"))
        )
        if os.path.exists(os.path.join(STATIC_FOLDER, "index.html")):
            STATIC_FOLDER_FOUND = True
            if DEBUG:
                print(
                    f"Static folder found using importlib.resources.path: {STATIC_FOLDER}"
                )
    except (
        ImportError,
        ModuleNotFoundError,
        AttributeError,
        ValueError,
        FileNotFoundError,
    ) as e:
        print(f"importlib.resources.path approach failed: {e}")

# Fallback to relative path for development
if not STATIC_FOLDER_FOUND:
    STATIC_FOLDER = "../../../webclient/dist"
    if DEBUG:
        print(f"Falling back to development path: {STATIC_FOLDER}")

    # Check if this path exists
    abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), STATIC_FOLDER))
    if os.path.exists(os.path.join(abs_path, "index.html")):
        if DEBUG:
            print(f"Development static folder found at: {abs_path}")
    else:
        # Always print warnings even in non-debug mode
        print(f"WARNING: Development static folder not found at: {abs_path}")
