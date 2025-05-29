#!/usr/bin/env python
"""
Gunicorn configuration for Renardo Web Server
"""
import os
import renardo.settings_manager

# Import the settings for webserver
from renardo.settings_manager import settings

# Determine the debug mode
debug_mode = settings.get("webserver.FLASK_DEBUG", False)

# Get port and host from settings with fallback to environment variables
port = int(os.environ.get("PORT", settings.get("webserver.PORT", 12345)))
host = os.environ.get("HOST", settings.get("webserver.HOST", "0.0.0.0"))

# Bind to a socket
bind = f"{host}:{port}"

# Worker configuration
workers = 1  # Using 1 process as requested
worker_class = "gevent"  # Using gevent for WebSocket support
threads = 10  # Number of threads per worker as requested

# Timeout configuration for WebSockets
timeout = 120  # 2 minutes timeout
keepalive = 5  # How long to wait for requests on a Keep-Alive connection

# Server mechanics
daemon = False
pidfile = "gunicorn.pid"

# Logging based on debug mode
accesslog = "-" if debug_mode else None  # Only log access in debug mode
errorlog = "-"  # Always log errors to stderr
loglevel = "debug" if debug_mode else "warning"

# Process naming
proc_name = "renardo_gunicorn"


# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    if debug_mode:
        print("Starting Renardo with Gunicorn")


def on_exit(server):
    """Called just before exiting."""
    if debug_mode:
        print("Shutting down Renardo Gunicorn server")

    # Send shutdown message to all connected clients
    if settings.get("webserver.AUTOCLOSE_WEBCLIENT", True):
        from renardo.webserver.websocket_utils import broadcast_to_clients

        broadcast_to_clients(
            {"type": "server_shutdown", "message": "Server is shutting down"}
        )
        # Give clients a moment to process the shutdown message
        import time

        time.sleep(0.5)


def post_fork(server, worker):
    """Called just after a worker has been forked."""
    if debug_mode:
        print(f"Worker spawned (pid: {worker.pid})")


def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    if debug_mode:
        print("Worker initialized")
