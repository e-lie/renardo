"""
Service for managing application state

This module delegates state management to the StateManager class from RenardoApp.
It maintains the same API for backward compatibility.
"""
from datetime import datetime

# Prevent circular imports with lazy loading
def _get_state_manager():
    """Get the StateManager instance from RenardoApp"""
    # Import locally to avoid circular imports
    from renardo.renardo_app import get_instance
    app = get_instance()
    return app.state_manager

def get_state():
    """
    Get current application state
    
    Returns:
        dict: Current state
    """
    return _get_state_manager().get_state()


def increment_counter():
    """
    Increment the counter in the state
    
    Returns:
        int: New counter value
    """
    return _get_state_manager().increment_counter()


def update_state(key, value):
    """
    Update a specific state value
    
    Args:
        key (str): State key to update
        value: New value
    
    Returns:
        dict: Updated state
    """
    return _get_state_manager().update_state(key, value)


def get_renardo_status():
    """
    Get Renardo initialization status
    
    Returns:
        dict: Renardo initialization status
    """
    return _get_state_manager().get_renardo_status()


def update_renardo_init_status(component, status):
    """
    Update Renardo initialization status
    
    Args:
        component (str): Component to update
        status (bool): New status
        
    Returns:
        dict: Updated Renardo initialization status
    """
    return _get_state_manager().update_renardo_init_status(component, status)


def get_runtime_status():
    """
    Get Renardo runtime status
    
    Returns:
        dict: Renardo runtime status
    """
    return _get_state_manager().get_runtime_status()


def update_runtime_status(component, status):
    """
    Update Renardo runtime status
    
    Args:
        component (str): Component to update (scBackendRunning or renardoRuntimeRunning)
        status (bool): New status
        
    Returns:
        dict: Updated Renardo runtime status
    """
    return _get_state_manager().update_runtime_status(component, status)


def add_log_message(message, level="INFO"):
    """
    Add a log message
    
    Args:
        message (str): Log message
        level (str): Log level (INFO, WARN, ERROR, SUCCESS)
        
    Returns:
        dict: Added log message
    """
    return _get_state_manager().add_log_message(message, level)


def get_log_messages():
    """
    Get all log messages
    
    Returns:
        list: All log messages
    """
    return _get_state_manager().get_log_messages()


# Reset the state (useful for testing)
def reset_state():
    """
    Reset state to default values
    
    Returns:
        dict: Reset state
    """
    return _get_state_manager().reset_state()