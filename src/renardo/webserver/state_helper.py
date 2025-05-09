"""
Service for managing application state helper functions

This module delegates state management to the StateManager class from RenardoApp.
It maintains the same API for backward compatibility.
"""
from datetime import datetime

def get_state_manager():
    """
    Get the StateManager instance from RenardoApp
    
    Returns:
        StateManager: The StateManager instance
    """
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
    return get_state_manager().get_state()


def increment_counter():
    """
    Increment the counter in the state
    
    Returns:
        int: New counter value
    """
    return get_state_manager().increment_counter()


def update_state(key, value):
    """
    Update a specific state value
    
    Args:
        key (str): State key to update
        value: New value
    
    Returns:
        dict: Updated state
    """
    state_manager = get_state_manager()
    
    # If the method exists, use it, otherwise implement behavior directly
    if hasattr(state_manager, 'update_state'):
        return state_manager.update_state(key, value)
    else:
        # Direct implementation as fallback
        state = state_manager.get_state()
        state[key] = value
        return state


def get_renardo_status():
    """
    Get Renardo initialization status
    
    Returns:
        dict: Renardo initialization status
    """
    return get_state_manager().get_renardo_status()


def update_renardo_init_status(component, status):
    """
    Update Renardo initialization status
    
    Args:
        component (str): Component to update
        status (bool): New status
        
    Returns:
        dict: Updated Renardo initialization status
    """
    return get_state_manager().update_renardo_init_status(component, status)

def add_log_message(message, level="INFO"):
    """
    Add a log message
    
    Args:
        message (str): Log message
        level (str): Log level (INFO, WARN, ERROR, SUCCESS)
        
    Returns:
        dict: Added log message
    """
    return get_state_manager().add_log_message(message, level)


def get_log_messages():
    """
    Get all log messages
    
    Returns:
        list: All log messages
    """
    return get_state_manager().get_log_messages()


# Reset the state (useful for testing)
def reset_state():
    """
    Reset state to default values
    
    Returns:
        dict: Reset state
    """
    return get_state_manager().reset_state()