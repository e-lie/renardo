#!/usr/bin/env python
"""
Gunicorn configuration for Renardo Web Server
"""

# Bind to a socket
bind = "0.0.0.0:5000"  # Same port as the default Flask app

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

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"

# Process naming
proc_name = "renardo_gunicorn"

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("Starting Renardo with Gunicorn")

def on_exit(server):
    """Called just before exiting."""
    print("Shutting down Renardo Gunicorn server")

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    print(f"Worker spawned (pid: {worker.pid})")

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    print("Worker initialized")