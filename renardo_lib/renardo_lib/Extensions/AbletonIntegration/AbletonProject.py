"""
AbletonProject - Main class for managing Ableton Live integration
Scans the Live set and creates a mapping of tracks, devices, and parameters
"""

import live
from typing import Dict, Optional, List
import re
import threading
import time
from renardo_lib.TimeVar import TimeVar


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
        self._set = live.Set(scan=scan)
        self._track_map = {}
        self._parameter_map = {}
        self._clip_map = {}  # Maps track_name -> clip inventory
        self._instruments = {}

        # TimeVar automation support
        self._timevar_params = {}  # Maps param_name -> TimeVar instance
        self._timevar_lock = threading.Lock()
        self._timevar_thread = None
        self._timevar_running = False

        if scan:
            self.scan_tracks()

        # Start TimeVar update thread
        self.start_timevar_thread()
    
    @property
    def set(self):
        """Access to underlying pylive Set object"""
        return self._set

    def _scan_clips(self, track, track_name: str):
        """
        Scan all clips on a track and build clip inventory

        Args:
            track: pylive Track object
            track_name: Snake_case track name
        """
        self._clip_map[track_name] = {
            'by_index': {},  # slot_idx -> clip info
            'by_name': {},   # clip_name (snake_case) -> clip info
            'by_original_name': {}  # original clip name -> clip info
        }

        # Check if track has clips attribute
        if not hasattr(track, 'clips'):
            return

        # Scan clips - pylive provides clips as a list
        try:
            for clip_idx, clip in enumerate(track.clips):
                if clip is not None:
                    clip_name_snake = make_snake_name(clip.name)
                    clip_info = {
                        'slot_index': clip_idx,
                        'clip': clip,
                        'name': clip.name,
                        'name_snake': clip_name_snake
                    }

                    # Store by index, snake_case name, and original name
                    self._clip_map[track_name]['by_index'][clip_idx] = clip_info
                    self._clip_map[track_name]['by_name'][clip_name_snake] = clip_info
                    self._clip_map[track_name]['by_original_name'][clip.name] = clip_info
        except Exception as e:
            # Silently ignore if clips scanning fails
            pass

    def scan_tracks(self, max_tracks: int = 16):
        """
        Scan the first N MIDI tracks and build parameter maps

        Args:
            max_tracks: Maximum number of tracks to scan (default 16)
        """
        self._track_map.clear()
        self._parameter_map.clear()
        self._clip_map.clear()

        # The set was already scanned in __init__, so tracks are available

        track_count = 0
        for track_idx, track in enumerate(self._set.tracks):
            # Only process MIDI tracks
            if not track.is_midi_track or track_count >= max_tracks:
                continue

            track_name = make_snake_name(track.name)
            self._track_map[track_name] = {
                'index': track_idx,
                'track': track,
                'devices': {}
            }

            # Scan clips on this track
            self._scan_clips(track, track_name)

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
                        'value': parameter._value  # Current value, no default_value in pylive
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
    
    def get_parameter_info(self, param_fullname: str, track_name: str = None) -> Optional[Dict]:
        """
        Get parameter information from the flattened parameter map

        Args:
            param_fullname: Parameter name (e.g., "operator_cutoff" or "cutoff")
            track_name: Optional track name to scope the search

        Returns:
            Dictionary with parameter info or None if not found
        """
        # Try direct lookup first (full track_device_param format)
        result = self._parameter_map.get(param_fullname)
        if result:
            return result

        # If track_name provided, try lookup with shortcuts
        if track_name:
            track_snake = make_snake_name(track_name)

            # Try with track prefix: track_device_param or track_param
            full_with_track = f"{track_snake}_{param_fullname}"
            result = self._parameter_map.get(full_with_track)
            if result:
                return result

            # Try as device_param (without track prefix)
            # Search for any param that ends with _param_fullname in this track
            track_info = self._track_map.get(track_snake)
            if track_info:
                # Look for device_param pattern
                for full_param_name in self._parameter_map:
                    if full_param_name.startswith(track_snake + "_") and full_param_name.endswith("_" + param_fullname):
                        return self._parameter_map[full_param_name]

                # Shortcut: Try first device if param name has no device prefix
                if "_" not in param_fullname and len(track_info['devices']) > 0:
                    # Get first device
                    first_device_name = list(track_info['devices'].keys())[0]
                    first_device_param = f"{track_snake}_{first_device_name}_{param_fullname}"
                    result = self._parameter_map.get(first_device_param)
                    if result:
                        return result

        return None

    def freeze_timevars_for_track(self, track_name: str) -> None:
        """
        Freeze all TimeVar parameters for a given track.
        Replaces TimeVars with their current fixed value.

        Args:
            track_name: Snake_case track name
        """
        with self._timevar_lock:
            params_to_freeze = []
            for param_name, (timevar, parameter) in list(self._timevar_params.items()):
                # Check if this parameter belongs to the specified track
                if param_name.startswith(track_name + "_") or self._parameter_map.get(param_name, {}).get('track_snake') == track_name:
                    params_to_freeze.append((param_name, timevar, parameter))

            # Remove from timevar tracking and set to current value
            for param_name, timevar, parameter in params_to_freeze:
                # Get current value and freeze it
                current_value = float(timevar.now())
                current_value = max(0.0, min(1.0, current_value))
                frozen_value = parameter.min + (current_value * (parameter.max - parameter.min))

                # Set the frozen value
                parameter.value = frozen_value

                # Remove from TimeVar tracking
                self._timevar_params.pop(param_name, None)

    def set_parameter(self, param_fullname: str, value, track_name: str = None) -> bool:
        """
        Set a parameter value by its full name

        Args:
            param_fullname: Parameter name (e.g., "operator_cutoff" or "cutoff")
            value: Parameter value (will be scaled to parameter range) or TimeVar
            track_name: Optional track name to scope the search

        Returns:
            True if parameter was set, False if not found
        """
        param_info = self.get_parameter_info(param_fullname, track_name)
        if not param_info:
            return False

        parameter = param_info['parameter']

        # Check if value is a TimeVar (linvar, sinvar, expvar, etc.)
        if isinstance(value, TimeVar):
            # Register TimeVar for continuous updates
            with self._timevar_lock:
                self._timevar_params[param_fullname] = (value, parameter)
            # Set initial value
            current_value = float(value.now())
            # Clamp to 0-1 and normalize to parameter range
            current_value = max(0.0, min(1.0, current_value))
            value = parameter.min + (current_value * (parameter.max - parameter.min))
            parameter.value = value
            return True

        # Handle Pattern objects
        if hasattr(value, '__iter__') and not isinstance(value, str):
            try:
                # Try to get first element
                value = value[0] if hasattr(value, '__getitem__') else parameter.min
            except (IndexError, TypeError):
                value = parameter.min

        # Convert to float and clamp to 0-1 range
        value = float(value)
        value = max(0.0, min(1.0, value))

        # Normalize to parameter's min/max range (0 = min, 1 = max)
        value = parameter.min + (value * (parameter.max - parameter.min))

        # Set the parameter and remove from TimeVar tracking if it was there
        with self._timevar_lock:
            self._timevar_params.pop(param_fullname, None)

        parameter.value = value
        return True
    
    def get_track(self, track_name: str):
        """Get a track by name"""
        track_info = self._track_map.get(make_snake_name(track_name))
        return track_info['track'] if track_info else None

    def get_midi_tracks(self) -> List[str]:
        """Get list of available MIDI track names"""
        return list(self._track_map.keys())

    def trigger_clip(self, track_name: str, clip_identifier) -> bool:
        """
        Trigger a clip on a track by name (original or snake_case) or by index

        Args:
            track_name: Snake_case track name
            clip_identifier: Can be:
                - int: clip slot index (0-based)
                - str: clip name (original or snake_case)

        Returns:
            True if clip was triggered, False if not found
        """
        track_snake = make_snake_name(track_name)
        clip_inventory = self._clip_map.get(track_snake)

        if not clip_inventory:
            return False

        clip_info = None

        # Try lookup by type
        if isinstance(clip_identifier, int):
            # Lookup by index
            clip_info = clip_inventory['by_index'].get(clip_identifier)
        elif isinstance(clip_identifier, str):
            # Try snake_case name first, then original name
            clip_info = clip_inventory['by_name'].get(clip_identifier)
            if not clip_info:
                clip_info = clip_inventory['by_original_name'].get(clip_identifier)

        if not clip_info:
            return False

        # Trigger the clip (fire method)
        try:
            clip_info['clip'].fire()
            return True
        except Exception as e:
            print(f"Error triggering clip: {e}")
            return False

    def get_clips(self, track_name: str) -> Optional[Dict]:
        """
        Get clip inventory for a track

        Args:
            track_name: Track name (original or snake_case)

        Returns:
            Dictionary with clip inventory or None if track not found
        """
        track_snake = make_snake_name(track_name)
        return self._clip_map.get(track_snake)
    
    def register_instrument(self, track_name: str, instrument):
        """Register an AbletonInstrument instance for a track"""
        self._instruments[make_snake_name(track_name)] = instrument
    
    def get_instrument(self, track_name: str):
        """Get registered AbletonInstrument for a track"""
        return self._instruments.get(make_snake_name(track_name))
    
    def start_timevar_thread(self):
        """Start the TimeVar update thread (100Hz update rate)"""
        if self._timevar_thread is not None:
            return  # Already running

        self._timevar_running = True
        self._timevar_thread = threading.Thread(target=self._timevar_update_loop, daemon=True)
        self._timevar_thread.start()

    def stop_timevar_thread(self):
        """Stop the TimeVar update thread"""
        self._timevar_running = False
        if self._timevar_thread is not None:
            self._timevar_thread.join(timeout=1.0)
            self._timevar_thread = None

    def _timevar_update_loop(self):
        """Update loop that runs at 100Hz to update TimeVar parameters"""
        update_interval = 0.003333  # 300Hz = 3.333ms interval

        while self._timevar_running:
            start_time = time.time()

            # Update all registered TimeVar parameters
            with self._timevar_lock:
                params_to_update = list(self._timevar_params.items())

            for param_name, (timevar, parameter) in params_to_update:
                try:
                    # Get current TimeVar value
                    current_value = float(timevar.now())

                    # Clamp to 0-1 and normalize to parameter range
                    current_value = max(0.0, min(1.0, current_value))
                    normalized_value = parameter.min + (current_value * (parameter.max - parameter.min))

                    # Update parameter in Live
                    parameter.value = normalized_value
                except Exception as e:
                    # Silently ignore errors to avoid breaking the update loop
                    pass

            # Sleep for the remaining time to maintain 100Hz
            elapsed = time.time() - start_time
            sleep_time = max(0, update_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def print_parameter_map(self):
        """Print the parameter map for debugging"""
        print("=== Ableton Parameter Map ===")
        for track_name, track_info in self._track_map.items():
            print(f"\nTrack: {track_name} (index: {track_info['index']})")

            # Print clips
            clip_inventory = self._clip_map.get(track_name)
            if clip_inventory and clip_inventory['by_index']:
                print(f"  Clips:")
                for slot_idx, clip_info in sorted(clip_inventory['by_index'].items()):
                    print(f"    [{slot_idx}] {clip_info['name']} (snake: {clip_info['name_snake']})")

            # Print devices
            for device_name, device_info in track_info['devices'].items():
                print(f"  Device: {device_name} (index: {device_info['index']})")
                for param_name, param_info in device_info['parameters'].items():
                    print(f"    {param_name}: min={param_info['min']}, max={param_info['max']}, value={param_info['value']}")

    def __del__(self):
        """Cleanup when the object is destroyed"""
        self.stop_timevar_thread()