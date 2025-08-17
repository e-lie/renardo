"""
Utility functions for reaside.
"""

from typing import Tuple, Optional
from renardo.logger import get_logger

logger = get_logger('reaside.utils')


def split_param_name(param_fullname: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Split a parameter name into FX name and parameter name.
    
    Args:
        param_fullname: Full parameter name in format "fx_name_param_name"
        
    Returns:
        Tuple of (fx_name, param_name). Returns (None, param_fullname) if no split possible.
        
    Examples:
        split_param_name("rea_eq_gain") -> ("rea_eq", "gain")
        split_param_name("reverb_room_size") -> ("reverb_room", "size")
        split_param_name("gain") -> (None, "gain")
        split_param_name("my_fx_param_value") -> ("my_fx_param", "value")
    """
    if '_' not in param_fullname:
        return None, param_fullname
    
    parts = param_fullname.split('_')
    if len(parts) < 2:
        return None, param_fullname
    
    # Last part is the parameter name, everything else is the FX name
    fx_name = '_'.join(parts[:-1])
    param_name = parts[-1]
    
    return fx_name, param_name


def normalize_fx_name(fx_name: str) -> str:
    """
    Normalize an FX name to match reaside's snake_case convention.
    
    Args:
        fx_name: Original FX name
        
    Returns:
        Normalized snake_case name
        
    Examples:
        normalize_fx_name("VST: ReaEQ (Cockos)") -> "rea_eq"
        normalize_fx_name("ReaComp") -> "rea_comp"
        normalize_fx_name("My Custom FX") -> "my_custom_fx"
    """
    import re
    
    # Remove common prefixes and suffixes
    name = re.sub(r'^(VST3?i?:?\s*|AU:?\s*|JS:?\s*|VST:?\s*)', '', fx_name)
    name = re.sub(r'\s*\([^)]*\)\s*$', '', name)  # Remove trailing parentheses
    
    # Convert to snake_case
    name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)  # camelCase to snake_case
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)  # Replace special chars with _
    name = re.sub(r'_+', '_', name)  # Collapse multiple underscores
    name = name.strip('_').lower()  # Remove leading/trailing _ and lowercase
    
    return name or 'unnamed'


def find_fx_by_param_name(track, param_fullname: str):
    """
    Find an FX object and parameter by full parameter name.
    Uses the same logic as list_parameters(): first FX has no prefix, others are prefixed.
    
    Args:
        track: ReaTrack instance
        param_fullname: Full parameter name like "fx_name_param_name" or "param_name" for first FX
        
    Returns:
        Tuple of (fx_object, param_object) or (None, None) if not found
    """
    fx_list = track.list_fx()
    if not fx_list:
        return None, None
    
    # First, try to find parameter in first FX (no prefix)
    first_fx = fx_list[0]
    if param_fullname in first_fx.params:
        return first_fx, first_fx.params[param_fullname]
    
    # Then try to find parameter with FX prefix in other FX
    for fx_index, fx in enumerate(fx_list):
        if fx_index == 0:
            continue  # Already checked first FX
        
        fx_name = fx.snake_name
        # Check if param_fullname starts with this FX name + underscore
        expected_prefix = f"{fx_name}_"
        
        if param_fullname.startswith(expected_prefix):
            param_name = param_fullname[len(expected_prefix):]
            if param_name in fx.params:
                return fx, fx.params[param_name]
    
    # Fallback to original logic for backward compatibility
    fx_name, param_name = split_param_name(param_fullname)
    
    # If no fx_name is specified, use the first FX on the track
    if not fx_name:
        if first_fx and param_name in first_fx.params:
            return first_fx, first_fx.params[param_name]
        return first_fx, None
    
    # Try to find FX by name (try both original and normalized names)
    fx_obj = track.get_fx_by_name(fx_name)
    if not fx_obj:
        # Try with normalized name
        normalized_name = normalize_fx_name(fx_name)
        fx_obj = track.get_fx_by_name(normalized_name)
    
    if not fx_obj:
        return None, None
    
    # Try to find parameter
    if param_name in fx_obj.params:
        return fx_obj, fx_obj.params[param_name]
    
    return fx_obj, None


def set_fx_parameter(track, param_fullname: str, value) -> bool:
    """
    Set an FX parameter value by full parameter name.
    
    Args:
        track: ReaTrack instance
        param_fullname: Full parameter name like "fx_name_param_name"
        value: Parameter value to set
        
    Returns:
        True if parameter was set successfully, False otherwise
    """
    fx_obj, param_obj = find_fx_by_param_name(track, param_fullname)
    
    if param_obj:
        try:
            param_obj.set_value(value)
            return True
        except Exception as e:
            print(f"Failed to set parameter {param_fullname} to {value}: {e}")
            return False
    
    return False


def get_fx_parameter(track, param_fullname: str):
    """
    Get an FX parameter value by full parameter name.
    
    Args:
        track: ReaTrack instance
        param_fullname: Full parameter name like "fx_name_param_name"
        
    Returns:
        Parameter value or None if not found
    """
    fx_obj, param_obj = find_fx_by_param_name(track, param_fullname)
    
    if param_obj:
        try:
            return param_obj.get_value()
        except Exception as e:
            print(f"Failed to get parameter {param_fullname}: {e}")
            return None
    
    return None


def enable_fx(track, fx_name: str, enabled: bool = True) -> bool:
    """
    Enable or disable an FX by name.
    
    Args:
        track: ReaTrack instance
        fx_name: Name of the FX to enable/disable
        enabled: True to enable, False to disable
        
    Returns:
        True if operation was successful, False otherwise
    """
    fx_obj = track.get_fx_by_name(fx_name)
    if not fx_obj:
        # Try with normalized name
        normalized_name = normalize_fx_name(fx_name)
        fx_obj = track.get_fx_by_name(normalized_name)
    
    if fx_obj:
        try:
            # Use the existing 'on' parameter that's automatically created for each FX
            if 'on' in fx_obj.params:
                # Set the enabled state (1.0 for enabled, 0.0 for disabled)
                fx_obj.params['on'].set_value(1.0 if enabled else 0.0)
                return True
            else:
                logger.error(f"FX {fx_name} does not have an 'on' parameter")
                return False
            
        except Exception as e:
            logger.error(f"Failed to {'enable' if enabled else 'disable'} FX {fx_name}: {e}")
            return False
    
    return False


def list_fx_parameters(track, fx_name: str) -> list:
    """
    List all parameters for a given FX.
    
    Args:
        track: ReaTrack instance
        fx_name: Name of the FX
        
    Returns:
        List of parameter names, or empty list if FX not found
    """
    fx_obj = track.get_fx_by_name(fx_name)
    if not fx_obj:
        # Try with normalized name
        normalized_name = normalize_fx_name(fx_name)
        fx_obj = track.get_fx_by_name(normalized_name)
    
    if fx_obj:
        try:
            if hasattr(fx_obj, 'list_params'):
                params = fx_obj.list_params()
                return [param.name for param in params]
        except Exception as e:
            print(f"Failed to list parameters for FX {fx_name}: {e}")
    
    return []