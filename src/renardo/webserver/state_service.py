"""
Service for managing application state
"""
# Singleton state object
_state = {
    "counter": 0,
    "welcome_text": "Welcome to the Flask + Svelte WebSocket App!"
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


# Reset the state (useful for testing)
def reset_state():
    """
    Reset state to default values

    Returns:
        dict: Reset state
    """
    _state["counter"] = 0
    return _state