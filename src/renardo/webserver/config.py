"""
Configuration settings for the Flask application
"""
import os

# Server settings
DEBUG = True
HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 5000))

# WebSocket settings
WEBSOCKET_ROUTE = '/ws'
PING_INTERVAL = 25  # seconds

# Path settings
STATIC_FOLDER = "../../../webclient/dist"