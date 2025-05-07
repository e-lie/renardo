#!/usr/bin/env python
"""
WSGI entry point for the Renardo web application.
This file serves as the entry point for Gunicorn to serve the Flask application.
"""

from gevent import monkey

# Apply gevent monkey patch to make WebSockets work with Gunicorn+gevent
monkey.patch_all()

from renardo.renardo_app import RenardoApp

# Get the RenardoApp instance
app_instance = RenardoApp.get_instance()

# Create the Flask web application instance
application = app_instance.create_webapp_instance()

# This is the WSGI entry point for Gunicorn
app = application

# Ensure WebSockets are properly initialized
# Flask-Sock will handle the WebSocket connections with gevent

if __name__ == "__main__":
    # This code will not run when using Gunicorn
    # It's here for development/testing purposes
    app_instance.launch()