"""REAPER parameter management for reaside."""

from typing import Optional, Union, Any
from enum import Enum
from ..tools.reaper_client import ReaperClient
from .timevar_manager import get_timevar_manager
from renardo.logger import get_logger

logger = get_logger('reaside.core.param')


class ReaParamState(Enum):
    """Parameter state enumeration."""
    NORMAL = "normal"
    VAR1 = "var1"
    VAR2 = "var2"


class ReaParam:
    """Represents a REAPER FX parameter."""
    
    def __init__(self, client: ReaperClient, track_index: int, fx_index: int, 
                 param_index: int, name: str, reaper_name: str, use_osc: bool = True,
                 initial_value: float = None, min_value: float = 0.0, max_value: float = 1.0):
        """Initialize ReaParam instance."""
        self.client = client
        self.track_index = track_index
        self.fx_index = fx_index
        self.param_index = param_index
        self.name = name  # snake_case name
        self.reaper_name = reaper_name  # original REAPER name
        self.use_osc = use_osc
        self.min_value = min_value
        self.max_value = max_value
        self.state = ReaParamState.NORMAL
        
        if initial_value is not None:
            self.value = initial_value
        else:
            self.value = 0.0
            self._update_value()
    
    def _update_value(self):
        """Update parameter value from REAPER."""
        if self.param_index == -1:  # Special case for FX enabled state
            track_obj = self.client.call_reascript_function("GetTrack", 0, self.track_index)
            if track_obj:
                self.value = float(self.client.call_reascript_function("TrackFX_GetEnabled", track_obj, self.fx_index))
        else:
            track_obj = self.client.call_reascript_function("GetTrack", 0, self.track_index)
            if track_obj:
                self.value = self.client.call_reascript_function("TrackFX_GetParam", track_obj, self.fx_index, self.param_index)
    
    def get_value(self) -> float:
        """Get current parameter value."""
        if self.use_osc and hasattr(self.client, 'send_osc_message'):
            # For OSC, we rely on cached values updated by OSC callbacks
            # This avoids expensive ReaScript calls
            return self.value
        else:
            # Update value from REAPER for non-OSC usage
            self._update_value()
            return self.value
    
    def update_from_osc(self, value: float):
        """Update parameter value from OSC callback."""
        self.value = value
    
    def __float__(self) -> float:
        """Allow parameter to be used as a float."""
        return self.get_value()
    
    def __repr__(self) -> str:
        return f"ReaParam('{self.name}', {self.value:.3f})"
    
    def __str__(self) -> str:
        return f"{self.reaper_name}: {self.value:.3f}"
    
    def set_value(self, value: Union[float, Any]):
        """
        Set parameter value directly in REAPER or bind a TimeVar for continuous updates.
        
        Args:
            value: Either a float value or a TimeVar object for continuous updates
        """
        # Check if value is a TimeVar-like object
        if self._is_timevar(value):
            # Bind TimeVar for continuous updates
            timevar_manager = get_timevar_manager()
            timevar_manager.bind_timevar(self, value)
            return
        
        # Clear any existing TimeVar binding
        timevar_manager = get_timevar_manager()
        if timevar_manager.is_param_bound(self):
            timevar_manager.unbind_param(self)
        
        # Normal float value handling
        self._set_value_internal(float(value))
    
    def _set_value_internal(self, value: float):
        """
        Internal method to set value without TimeVar detection.
        Used by TimeVarManager to avoid infinite loops.
        """
        # Clamp value to valid range
        value = max(self.min_value, min(self.max_value, value))
        self.value = value
        
        if self.use_osc and hasattr(self.client, 'send_osc_message'):
            # Try OSC first for better performance
            osc_success = False
            if self.param_index == -1:  # Special case for FX enabled state
                # OSC message for FX enable/disable (bypass) - OSC uses 1-based indexing
                osc_address = f"/track/{self.track_index + 1}/fx/{self.fx_index + 1}/bypass"
                bypass_value = int(value > 0.5)  # REAPER OSC: 1 = enabled, 0 = bypassed
                osc_success = self.client.send_osc_message(osc_address, bypass_value)
                if osc_success:
                    bypass_state = "ENABLED" if bypass_value == 1 else "BYPASSED"
                    logger.debug(f"Sent OSC bypass: {osc_address} = {bypass_value} ({bypass_state})")
            else:
                # OSC message for parameter value - OSC uses 1-based indexing for FX and params
                osc_address = f"/track/{self.track_index + 1}/fx/{self.fx_index + 1}/fxparam/{self.param_index + 1}/value"
                osc_success = self.client.send_osc_message(osc_address, value)
                if osc_success:
                    logger.debug(f"Sent OSC: {osc_address} = {value:.3f}")
            
            # If OSC succeeded, we're done
            if osc_success:
                return
        
        # Use ReaScript as fallback
        if self.param_index == -1:  # Special case for FX enabled state
            track_obj = self.client.call_reascript_function("GetTrack", 0, self.track_index)
            if track_obj:
                self.client.call_reascript_function("TrackFX_SetEnabled", track_obj, self.fx_index, value > 0.5)
        else:
            track_obj = self.client.call_reascript_function("GetTrack", 0, self.track_index)
            if track_obj:
                self.client.call_reascript_function("TrackFX_SetParam", track_obj, self.fx_index, self.param_index, value)
    
    def _is_timevar(self, value) -> bool:
        """
        Check if a value is a TimeVar-like object for continuous modulation.
        
        Args:
            value: Value to check
            
        Returns:
            True if value appears to be a TimeVar for continuous modulation
        """
        # Don't treat basic types as TimeVar
        if isinstance(value, (int, float, bool, str)):
            return False
        
        # Support renardo's TimeVar (var, linvar, expvar, sinvar)
        if hasattr(value, '__class__'):
            module = getattr(value.__class__, '__module__', '')
            class_name = value.__class__.__name__
            
            # Check for renardo TimeVar classes
            if 'renardo.lib.TimeVar' in module or class_name == 'TimeVar':
                # Make sure it has the now() method for evaluation
                if hasattr(value, 'now'):
                    return True
        
        # Check if it's specifically marked as a TimeVar for reaside
        if hasattr(value, '_is_reaside_timevar'):
            return True
        
        # Check for any object with now() method that looks like a TimeVar
        if hasattr(value, 'now') and callable(getattr(value, 'now')):
            return True
        
        return False
    
    def update_value(self):
        """Update parameter value from REAPER."""
        self._update_value()
    
    def get_formatted_value(self) -> str:
        """Get formatted parameter value as string."""
        if self.param_index == -1:  # Special case for FX enabled state
            return "On" if self.value > 0.5 else "Off"
        return self.client.get_fx_param_formatted(
            self.track_index, self.fx_index, self.param_index
        )
    
    def get_min_value(self) -> float:
        """Get minimum parameter value."""
        if self.param_index == -1:  # Special case for FX enabled state
            return 0.0
        return 0.0  # Default for normalized parameters
    
    def get_max_value(self) -> float:
        """Get maximum parameter value."""
        if self.param_index == -1:  # Special case for FX enabled state
            return 1.0
        return 1.0  # Default for normalized parameters
    
    def normalize_value(self, value: float) -> float:
        """Normalize value to 0.0-1.0 range."""
        min_val = self.get_min_value()
        max_val = self.get_max_value()
        return (value - min_val) / (max_val - min_val)
    
    def denormalize_value(self, normalized_value: float) -> float:
        """Denormalize value from 0.0-1.0 range."""
        min_val = self.get_min_value()
        max_val = self.get_max_value()
        return min_val + normalized_value * (max_val - min_val)
    
    def __str__(self) -> str:
        """String representation of parameter."""
        return f"ReaParam({self.name}={self.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"ReaParam(name='{self.name}', reaper_name='{self.reaper_name}', "
                f"value={self.value}, track={self.track_index}, fx={self.fx_index}, "
                f"param={self.param_index})")


class ReaSend(ReaParam):
    """Represents a REAPER track send parameter."""
    
    def __init__(self, client: ReaperClient, track_index: int, send_index: int, 
                 param_type: str, name: str):
        """Initialize ReaSend instance."""
        self.send_index = send_index
        self.param_type = param_type
        super().__init__(
            client=client,
            track_index=track_index,
            fx_index=-1,  # Not applicable for sends
            param_index=-1,  # Not applicable for sends
            name=name,
            reaper_name=f"Send {send_index} {param_type}"
        )
    
    def _update_value(self):
        """Update send parameter value from REAPER."""
        if self.param_type == "volume":
            self.value = self.client.get_send_volume(self.track_index, self.send_index)
        elif self.param_type == "pan":
            self.value = self.client.get_send_pan(self.track_index, self.send_index)
        elif self.param_type == "mute":
            self.value = float(self.client.get_send_mute(self.track_index, self.send_index))
        else:
            self.value = 0.0
    
    def set_value(self, value: Union[float, Any]):
        """
        Set send parameter value directly in REAPER or bind a TimeVar for continuous updates.
        
        Args:
            value: Either a float value or a TimeVar object for continuous updates
        """
        # Check if value is a TimeVar-like object
        if self._is_timevar(value):
            # Bind TimeVar for continuous updates
            timevar_manager = get_timevar_manager()
            timevar_manager.bind_timevar(self, value)
            return
        
        # Clear any existing TimeVar binding
        timevar_manager = get_timevar_manager()
        if timevar_manager.is_param_bound(self):
            timevar_manager.unbind_param(self)
        
        # Normal float value handling
        self._set_value_internal(float(value))
    
    def _set_value_internal(self, value: float):
        """
        Internal method to set value without TimeVar detection.
        Used by TimeVarManager to avoid infinite loops.
        """
        from renardo.logger import get_logger
        logger = get_logger('reaside.core.param')
        
        self.value = value
        if self.param_type == "volume":
            logger.info(f"ReaSend setting send volume: track {self.track_index}, send {self.send_index}, value {value}")
            self.client.set_send_volume(self.track_index, self.send_index, value)
        elif self.param_type == "pan":
            self.client.set_send_pan(self.track_index, self.send_index, value)
        elif self.param_type == "mute":
            self.client.set_send_mute(self.track_index, self.send_index, value > 0.5)
    
    def get_formatted_value(self) -> str:
        """Get formatted send parameter value."""
        if self.param_type == "volume":
            return f"{self.value:.2f} dB"
        elif self.param_type == "pan":
            return f"{self.value:.2f}"
        elif self.param_type == "mute":
            return "Muted" if self.value > 0.5 else "Unmuted"
        return str(self.value)
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"ReaSend(name='{self.name}', type='{self.param_type}', "
                f"value={self.value}, track={self.track_index}, send={self.send_index})")