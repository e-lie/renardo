"""
Service for managing application state
"""
from datetime import datetime

# Singleton state object
_state = {
    "counter": 0,
    "welcome_text": "Welcome to Renardo Web Interface",
    # Renardo initialization status
    "renardo_init": {
        "superColliderClasses": False,
        "samples": False,
        "instruments": False
    },
    # Log messages
    "log_messages": []
}


def get_state():
    """
    Get current application state

    Returns:
        dict: Current state
    """
    return _state


def increment_counter():
    """
    Increment the counter in the state

    Returns:
        int: New counter value
    """
    _state["counter"] += 1
    return _state["counter"]


def update_state(key, value):
    """
    Update a specific state value

    Args:
        key (str): State key to update
        value: New value

    Returns:
        dict: Updated state
    """
    if key in _state:
        _state[key] = value
    return _state


def get_renardo_status():
    """
    Get Renardo initialization status
    
    Returns:
        dict: Renardo initialization status
    """
    return _state["renardo_init"]


def update_renardo_init_status(component, status):
    """
    Update Renardo initialization status
    
    Args:
        component (str): Component to update
        status (bool): New status
        
    Returns:
        dict: Updated Renardo initialization status
    """
    if component in _state["renardo_init"]:
        _state["renardo_init"][component] = status
    
    return _state["renardo_init"]


def add_log_message(message, level="INFO"):
    """
    Add a log message
    
    Args:
        message (str): Log message
        level (str): Log level (INFO, WARN, ERROR, SUCCESS)
        
    Returns:
        dict: Added log message
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "level": level,
        "message": message
    }
    
    if "log_messages" not in _state:
        _state["log_messages"] = []
    
    _state["log_messages"].append(log_entry)
    
    # Keep only the 1000 most recent log messages
    if len(_state["log_messages"]) > 1000:
        _state["log_messages"] = _state["log_messages"][-1000:]
    
    return log_entry


def get_log_messages():
    """
    Get all log messages
    
    Returns:
        list: All log messages
    """
    if "log_messages" not in _state:
        _state["log_messages"] = []
    
    return _state["log_messages"]


# Reset the state (useful for testing)
def reset_state():
    """
    Reset state to default values

    Returns:
        dict: Reset state
    """
    _state["counter"] = 0
    _state["renardo_init"] = {
        "superColliderClasses": False,
        "samples": False,
        "instruments": False
    }
    _state["log_messages"] = []
    return _state