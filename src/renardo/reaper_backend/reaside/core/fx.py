"""REAPER FX management for reaside."""

import re
from typing import Dict, Any, Optional, List
from .param import ReaParam
from ..tools.reaper_client import ReaperClient


class ReaFX:
    """Represents a REAPER FX plugin."""
    
    def __init__(self, client: ReaperClient, track_index: int, fx_index: int, name: str = None, scan_data: Dict = None, track_ref=None):
        """Initialize ReaFX instance."""
        self.client = client
        self.track_index = track_index
        self.fx_index = fx_index
        self.name = name or f"fx_{fx_index}"
        self.reaper_name = name  # Store original REAPER name
        self.snake_name = self._make_snake_name(name) if name else f"fx_{fx_index}"
        self.params: Dict[str, ReaParam] = {}
        self.scan_data = scan_data
        self._track_ref = track_ref  # Reference to ReaTrack object
        
        if scan_data:
            self._init_params_from_scan(scan_data)
        else:
            self._init_params()
    
    def _make_snake_name(self, name: str) -> str:
        """Convert a name to snake_case."""
        if not name:
            return 'unnamed'
        
        # Remove common prefixes and suffixes
        name = re.sub(r'^(VST3?i?:?\s*|AU:?\s*|JS:?\s*|VST:?\s*)', '', name)
        name = re.sub(r'\s*\([^)]*\)\s*$', '', name)  # Remove trailing parentheses
        
        # Convert to snake_case
        name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)  # camelCase to snake_case
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)  # Replace special chars with _
        name = re.sub(r'_+', '_', name)  # Collapse multiple underscores
        name = name.strip('_').lower()  # Remove leading/trailing _ and lowercase
        
        return name or 'unnamed'
    
    def _init_params_from_scan(self, scan_data: Dict):
        """Initialize parameters from scan data (faster)."""
        # Create 'on' parameter for enabled/disabled state
        self.params['on'] = ReaParam(
            client=self.client,
            track_index=self.track_index,
            fx_index=self.fx_index,
            param_index=-1,  # Special index for FX enabled state
            name='on',
            reaper_name='FX Enabled',
            use_osc=True,
            track_ref=self._track_ref
        )
        
        # Create parameters from scan data
        for param_data in scan_data.get('params', []):
            param_name = param_data.get('name', f"param_{param_data['index']}")
            snake_name = self._make_snake_name(param_name)
            
            self.params[snake_name] = ReaParam(
                client=self.client,
                track_index=self.track_index,
                fx_index=self.fx_index,
                param_index=param_data['index'],
                name=snake_name,
                reaper_name=param_name,
                use_osc=True,
                initial_value=param_data.get('value', 0.0),
                min_value=param_data.get('min', 0.0),
                max_value=param_data.get('max', 1.0),
                track_ref=self._track_ref
            )
    
    def _init_params(self):
        """Initialize all parameters for this FX (legacy method)."""
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
            reaper_name='FX Enabled',
            use_osc=True,
            track_ref=self._track_ref
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
                reaper_name=param_name,
                use_osc=True,
                track_ref=self._track_ref
            )
    
    # Parameter access methods
    def get_param(self, param_name: str) -> Optional[ReaParam]:
        """Get parameter by snake_case name."""
        return self.params.get(param_name)
    
    def get_param_by_name(self, name: str) -> Optional[ReaParam]:
        """Get parameter by original name or snake_case name."""
        # Try snake_case first
        snake_name = self._make_snake_name(name)
        param = self.params.get(snake_name)
        if param:
            return param
        
        # Try exact match with original name
        for param in self.params.values():
            if hasattr(param, 'reaper_name') and param.reaper_name == name:
                return param
        
        return None
    
    def list_params(self) -> List[ReaParam]:
        """Get list of all parameters, ordered with regular parameters first."""
        # Separate regular parameters from special ones
        regular_params = []
        special_params = []
        
        for param in self.params.values():
            if param.param_index >= 0:  # Regular parameter
                regular_params.append(param)
            else:  # Special parameter (like 'on' for bypass)
                special_params.append(param)
        
        # Sort regular parameters by their param_index
        regular_params.sort(key=lambda p: p.param_index)
        
        # Return regular parameters first, then special parameters
        return regular_params + special_params
    
    def get_bypass_param(self) -> Optional[ReaParam]:
        """Get the FX bypass parameter."""
        return self.params.get('on')
    
    def set_enabled(self, enabled: bool):
        """Set FX enabled state."""
        bypass_param = self.get_bypass_param()
        if bypass_param:
            # For bypass param: 1.0 = enabled, 0.0 = bypassed
            bypass_param.set_value(1.0 if enabled else 0.0)
    
    def is_enabled(self) -> bool:
        """Check if FX is enabled."""
        bypass_param = self.get_bypass_param()
        if bypass_param:
            value = bypass_param.get_value()
            if isinstance(value, tuple):
                value = value[0]
            return value >= 0.5  # >= 0.5 means enabled
        return True  # Default to enabled if no bypass param
    
    
    def set_param(self, param_name: str, value: float):
        """Set parameter value by snake_case name."""
        param = self.params.get(param_name)
        if param:
            param.set_value(value)
        else:
            raise ValueError(f"Parameter '{param_name}' not found")
    
    def get_param_value(self, param_name: str) -> float:
        """Get parameter value by snake_case name."""
        param = self.params.get(param_name)
        if param:
            return param.get_value()
        else:
            raise ValueError(f"Parameter '{param_name}' not found")
    
    def __getattr__(self, name: str):
        """Allow accessing parameters by snake_case name as attributes."""
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        param = self.params.get(name)
        if param:
            return param
        
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
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

