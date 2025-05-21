"""
StateManager module for centralized state management
"""
from datetime import datetime


class StateManager:
    """
    Manages application state in an object-oriented way
    """
    
    def __init__(self):
        """Initialize the state manager with default values"""
        self._state = {
            "counter": 0,
            "welcome_text": "Welcome to Renardo Web Interface",
            # Renardo initialization status
            "renardo_init": {
                "superColliderClasses": False,
                "sclangCode": False,
                "samples": False,
                "instruments": False,
                "reaperPack": False
            },
            # Log messages
            "log_messages": []
        }
    
    def get_state(self):
        """
        Get current application state
        
        Returns:
            dict: Current state
        """
        return self._state
    
    def increment_counter(self):
        """
        Increment the counter in the state
        
        Returns:
            int: New counter value
        """
        self._state["counter"] += 1
        return self._state["counter"]
    
    def update_state(self, key, value):
        """
        Update a specific state value
        
        Args:
            key (str): State key to update
            value: New value
        
        Returns:
            dict: Updated state
        """
        if key in self._state:
            # If nested dictionary, merge instead of replace
            if isinstance(self._state[key], dict) and isinstance(value, dict):
                self._state[key].update(value)
            else:
                self._state[key] = value
        else:
            # If key doesn't exist, add it
            self._state[key] = value
        return self._state
    
    def get_renardo_status(self):
        """
        Get Renardo initialization status
        
        Returns:
            dict: Renardo initialization status
        """
        return self._state["renardo_init"]
    
    def update_renardo_init_status(self, component, status):
        """
        Update Renardo initialization status
        
        Args:
            component (str): Component to update
            status (bool): New status
            
        Returns:
            dict: Updated Renardo initialization status
        """
        if component in self._state["renardo_init"]:
            self._state["renardo_init"][component] = status
        
        return self._state["renardo_init"]
    

    
    def add_log_message(self, message, level="INFO"):
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
        
        if "log_messages" not in self._state:
            self._state["log_messages"] = []
        
        self._state["log_messages"].append(log_entry)
        
        # Keep only the 1000 most recent log messages
        if len(self._state["log_messages"]) > 1000:
            self._state["log_messages"] = self._state["log_messages"][-1000:]
        
        return log_entry
    
    def get_log_messages(self):
        """
        Get all log messages
        
        Returns:
            list: All log messages
        """
        if "log_messages" not in self._state:
            self._state["log_messages"] = []
        
        return self._state["log_messages"]
    
    def reset_state(self):
        """
        Reset state to default values
        
        Returns:
            dict: Reset state
        """
        self._state["counter"] = 0
        self._state["renardo_init"] = {
            "superColliderClasses": False,
            "sclangCode": False,
            "samples": False,
            "instruments": False,
            "reaperPack": False
        }
        self._state["log_messages"] = []
        return self._state