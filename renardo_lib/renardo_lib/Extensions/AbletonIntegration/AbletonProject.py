"""
AbletonProject - Main class for managing Ableton Live integration
Scans the Live set and creates a mapping of tracks, devices, and parameters
"""

import live
from typing import Dict, Optional, List
import re


def make_snake_name(name: str) -> str:
    """Convert Ableton object names to snake_case for parameter mapping"""
    # Remove special characters and convert to snake_case
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', '_', name)
    return name.lower()


class AbletonProject:
    """
    Wrapper class for pylive Set object with parameter mapping functionality
    """
    
    def __init__(self, scan: bool = True):
        """
        Initialize connection to Ableton Live set
        
        Args:
            scan: Whether to automatically scan tracks on initialization
        """
        self._set = live.Set()
        self._track_map = {}
        self._parameter_map = {}
        self._instruments = {}
        
        if scan:
            self.scan_tracks()
    
    @property
    def set(self):
        """Access to underlying pylive Set object"""
        return self._set
    
    def scan_tracks(self, max_tracks: int = 16):
        """
        Scan the first N MIDI tracks and build parameter maps
        
        Args:
            max_tracks: Maximum number of tracks to scan (default 16)
        """
        self._track_map.clear()
        self._parameter_map.clear()
        
        # Scan the set to populate tracks and devices
        self._set.scan(get_tracks=True, get_devices=True, get_clips=False)
        
        track_count = 0
        for track_idx, track in enumerate(self._set.tracks):
            # Only process MIDI tracks
            if not track.has_midi_input or track_count >= max_tracks:
                continue
            
            track_name = make_snake_name(track.name)
            self._track_map[track_name] = {
                'index': track_idx,
                'track': track,
                'devices': {}
            }
            
            # Scan devices on this track
            for device_idx, device in enumerate(track.devices):
                device_name = make_snake_name(device.name)
                
                self._track_map[track_name]['devices'][device_name] = {
                    'index': device_idx,
                    'device': device,
                    'parameters': {}
                }
                
                # Scan parameters on this device
                for param_idx, parameter in enumerate(device.parameters):
                    param_name = make_snake_name(parameter.name)
                    param_key = f"{track_name}_{device_name}_{param_name}"
                    
                    # Store parameter info in device map
                    self._track_map[track_name]['devices'][device_name]['parameters'][param_name] = {
                        'index': param_idx,
                        'parameter': parameter,
                        'min': parameter.min,
                        'max': parameter.max,
                        'default': parameter.default_value
                    }
                    
                    # Store flattened parameter map for quick lookup
                    self._parameter_map[param_key] = {
                        'track_idx': track_idx,
                        'device_idx': device_idx,
                        'param_idx': param_idx,
                        'track_name': track_name,
                        'device_name': device_name,
                        'param_name': param_name,
                        'parameter': parameter
                    }
            
            track_count += 1
    
    def get_parameter_info(self, param_fullname: str) -> Optional[Dict]:
        """
        Get parameter information from the flattened parameter map
        
        Args:
            param_fullname: Full parameter name (e.g., "bass_operator_cutoff")
            
        Returns:
            Dictionary with parameter info or None if not found
        """
        return self._parameter_map.get(param_fullname)
    
    def set_parameter(self, param_fullname: str, value: float) -> bool:
        """
        Set a parameter value by its full name
        
        Args:
            param_fullname: Full parameter name (e.g., "bass_operator_cutoff")
            value: Parameter value (will be scaled to parameter range)
            
        Returns:
            True if parameter was set, False if not found
        """
        param_info = self.get_parameter_info(param_fullname)
        if not param_info:
            return False
        
        parameter = param_info['parameter']
        
        # Scale value to parameter range
        if hasattr(value, '__iter__'):  # Handle patterns
            value = value[0] if len(value) > 0 else parameter.default_value
        
        # Clamp to parameter range
        value = max(parameter.min, min(parameter.max, float(value)))
        
        # Set the parameter
        parameter.value = value
        return True
    
    def get_track(self, track_name: str) -> Optional[live.Track]:
        """Get a track by name"""
        track_info = self._track_map.get(make_snake_name(track_name))
        return track_info['track'] if track_info else None
    
    def get_midi_tracks(self) -> List[str]:
        """Get list of available MIDI track names"""
        return list(self._track_map.keys())
    
    def register_instrument(self, track_name: str, instrument):
        """Register an AbletonInstrument instance for a track"""
        self._instruments[make_snake_name(track_name)] = instrument
    
    def get_instrument(self, track_name: str):
        """Get registered AbletonInstrument for a track"""
        return self._instruments.get(make_snake_name(track_name))
    
    def print_parameter_map(self):
        """Print the parameter map for debugging"""
        print("=== Ableton Parameter Map ===")
        for track_name, track_info in self._track_map.items():
            print(f"\nTrack: {track_name} (index: {track_info['index']})")
            for device_name, device_info in track_info['devices'].items():
                print(f"  Device: {device_name} (index: {device_info['index']})")
                for param_name, param_info in device_info['parameters'].items():
                    print(f"    {param_name}: min={param_info['min']}, max={param_info['max']}, default={param_info['default']}")