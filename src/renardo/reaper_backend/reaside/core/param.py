"""REAPER parameter management for reaside."""

from typing import Optional
from enum import Enum
from ..tools.reaper_client import ReaperClient


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
        if self.use_osc and hasattr(self.client, 'osc_client') and self.client.osc_client:
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
    
    def set_value(self, value: float):
        """Set parameter value directly in REAPER."""
        # Clamp value to valid range
        value = max(self.min_value, min(self.max_value, value))
        self.value = value
        
        if self.use_osc and hasattr(self.client, 'osc_client') and self.client.osc_client:
            # Try OSC first for better performance
            try:
                if self.param_index == -1:  # Special case for FX enabled state
                    # OSC message for FX enable/disable (bypass)
                    self.client.send_osc_message(f"/track/{self.track_index + 1}/fx/{self.fx_index}/bypass", int(value <= 0.5))
                else:
                    # OSC message for parameter value (using correct REAPER format)
                    self.client.send_osc_message(f"/track/{self.track_index + 1}/fx/{self.fx_index}/fxparam/{self.param_index}/value", value)
                return
            except Exception as e:
                # Fallback to ReaScript if OSC fails
                pass
        
        # Use ReaScript as fallback
        if self.param_index == -1:  # Special case for FX enabled state
            track_obj = self.client.call_reascript_function("GetTrack", 0, self.track_index)
            if track_obj:
                self.client.call_reascript_function("TrackFX_SetEnabled", track_obj, self.fx_index, value > 0.5)
        else:
            track_obj = self.client.call_reascript_function("GetTrack", 0, self.track_index)
            if track_obj:
                self.client.call_reascript_function("TrackFX_SetParam", track_obj, self.fx_index, self.param_index, value)
    
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
    
    def set_value(self, value: float):
        """Set send parameter value directly in REAPER."""
        self.value = value
        if self.param_type == "volume":
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