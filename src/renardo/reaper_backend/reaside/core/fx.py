"""REAPER FX management for reaside."""

from typing import Dict, Any, Optional, List
from .param import ReaParam
from ..tools.reaper_client import ReaperClient


class ReaFX:
    """Represents a REAPER FX plugin."""
    
    def __init__(self, client: ReaperClient, track_index: int, fx_index: int, name: str = None):
        """Initialize ReaFX instance."""
        self.client = client
        self.track_index = track_index
        self.fx_index = fx_index
        self.name = name or f"fx_{fx_index}"
        self.params: Dict[str, ReaParam] = {}
        self._init_params()
    
    def _init_params(self):
        """Initialize all parameters for this FX."""
        # Get track object
        track_obj = self.client.call_reascript_function("GetTrack", 0, self.track_index)
        if not track_obj:
            return
        
        # Get parameter count
        param_count = self.client.call_reascript_function("TrackFX_GetNumParams", track_obj, self.fx_index)
        
        # Create 'on' parameter for enabled/disabled state
        self.params['on'] = ReaParam(
            client=self.client,
            track_index=self.track_index,
            fx_index=self.fx_index,
            param_index=-1,  # Special index for FX enabled state
            name='on',
            reaper_name='FX Enabled'
        )
        
        # Create parameters for each FX parameter
        for i in range(param_count):
            param_name = self.client.call_reascript_function("TrackFX_GetParamName", track_obj, self.fx_index, i, "", 256)
            if isinstance(param_name, tuple):
                param_name = param_name[1] if len(param_name) > 1 else f"param_{i}"
            snake_name = self._make_snake_name(param_name)
            
            self.params[snake_name] = ReaParam(
                client=self.client,
                track_index=self.track_index,
                fx_index=self.fx_index,
                param_index=i,
                name=snake_name,
                reaper_name=param_name
            )
    
    def _make_snake_name(self, name: str) -> str:
        """Convert parameter name to snake_case."""
        import re
        # Replace spaces, parentheses, slashes, dots with underscores
        name = re.sub(r'[\s\(\)/\.]', '_', name)
        # Convert to lowercase
        name = name.lower()
        # Remove multiple underscores
        name = re.sub(r'_+', '_', name)
        # Remove leading/trailing underscores
        name = name.strip('_')
        return name
    
    def get_param(self, name: str) -> Optional[float]:
        """Get parameter value by name."""
        if name in self.params:
            return self.params[name].get_value()
        return None
    
    def set_param(self, name: str, value: float):
        """Set parameter value directly in REAPER."""
        if name in self.params:
            self.params[name].set_value(value)
    
    def update_params(self):
        """Update all parameters to their current values."""
        for param in self.params.values():
            param.update_value()
    
    def get_all_params(self) -> Dict[str, float]:
        """Get all parameter values with FX name prefix."""
        result = {}
        for param_name, param in self.params.items():
            prefixed_name = f"{self.name}_{param_name}"
            result[prefixed_name] = param.get_value()
        return result
    
    def is_enabled(self) -> bool:
        """Check if FX is enabled."""
        return self.params['on'].get_value() > 0.5
    
    def enable(self):
        """Enable FX."""
        self.set_param('on', 1.0)
    
    def disable(self):
        """Disable FX."""
        self.set_param('on', 0.0)
    
    def get_param_names(self) -> List[str]:
        """Get list of all parameter names."""
        return list(self.params.keys())

