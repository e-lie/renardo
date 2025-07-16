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
        # Get parameter count
        param_count = self.client.get_fx_param_count(self.track_index, self.fx_index)
        
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
            param_name = self.client.get_fx_param_name(self.track_index, self.fx_index, i)
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


class ReaFXGroup:
    """Represents a group of identical FX plugins."""
    
    def __init__(self, name: str):
        """Initialize ReaFXGroup."""
        self.name = name
        self.fx_list: List[ReaFX] = []
    
    def add_fx(self, fx: ReaFX):
        """Add FX to the group."""
        self.fx_list.append(fx)
    
    def get_param(self, name: str) -> Optional[float]:
        """Get parameter value from first FX in group."""
        if self.fx_list:
            return self.fx_list[0].get_param(name)
        return None
    
    def set_param(self, name: str, value: float):
        """Set parameter value for all FX in group."""
        for fx in self.fx_list:
            fx.set_param(name, value)
    
    def set_param_direct(self, name: str, value: float):
        """Set parameter value directly for all FX in group."""
        for fx in self.fx_list:
            fx.set_param(name, value)
    
    def update_params(self):
        """Update all parameters for all FX in group."""
        for fx in self.fx_list:
            fx.update_params()
    
    def get_all_params(self) -> Dict[str, float]:
        """Get all parameter values from first FX with group name prefix."""
        if not self.fx_list:
            return {}
        
        result = {}
        first_fx_params = self.fx_list[0].get_all_params()
        for param_name, value in first_fx_params.items():
            # Replace FX name with group name
            group_param_name = param_name.replace(f"{self.fx_list[0].name}_", f"{self.name}_")
            result[group_param_name] = value
        return result
    
    def enable_all(self):
        """Enable all FX in group."""
        for fx in self.fx_list:
            fx.enable()
    
    def disable_all(self):
        """Disable all FX in group."""
        for fx in self.fx_list:
            fx.disable()
    
    def get_param_names(self) -> List[str]:
        """Get list of all parameter names from first FX."""
        if self.fx_list:
            return self.fx_list[0].get_param_names()
        return []