"""Track-related functionality module."""

from renardo.logger import get_logger
import os
import re
from pathlib import Path
from typing import Optional, List, Union, Dict, Any

logger = get_logger('reaside.core.track')

class ReaTrack:
    """REAPER track."""
    
    def __init__(self, project, index):
        """Initialize the Track object."""
        self._project = project
        self._reaper = project._reaper
        self._client = project._client
        self._index = index
        self._items = {}  # Cache for Item objects
        self._scan_data = None  # Track scan data cache
        
        # FX storage - unified dict for both numeric index and snake_name access
        self.reafxs = {}  # Dict storing ReaFX objects by snake_name AND numeric index
        
        # Send storage - dict storing ReaSend objects by destination track name
        self.sends = {}  # Dict storing ReaSend objects for controlling send parameters
        
        # Perform initial scan to populate FX and parameters
        self._scan_track()
        
    def _scan_track(self):
        """Scan track to populate FX and parameter information via Rust OSC extension."""
        from ..tools.rust_osc_client import get_rust_osc_client
        rust_client = get_rust_osc_client()
        scan_result = rust_client.scan_track(self._index, timeout=3.0)
        
        if scan_result:
            self._scan_data = self._convert_rust_scan_to_legacy_format(scan_result)
            self._populate_reafxs()
            logger.debug(f"Track {self._index} scanned via Rust OSC extension")
        else:
            logger.error(f"Rust OSC scan failed for track {self._index}")
            self._scan_data = None

    def _convert_rust_scan_to_legacy_format(self, rust_data: dict) -> dict:
        """Convert Rust OSC scan format to legacy Lua scan format."""
        legacy_data = {
            "index": rust_data.get("index", self._index),
            "name": rust_data.get("name", ""),
            "volume": rust_data.get("volume", 1.0),
            "pan": rust_data.get("pan", 0.0),
            "mute": rust_data.get("mute", False),
            "solo": rust_data.get("solo", False),
            "rec_arm": rust_data.get("rec_arm", False),
            "rec_input": rust_data.get("rec_input", -1),
            "rec_mode": rust_data.get("rec_mode", 0),
            "rec_mon": rust_data.get("rec_mon", 0),
            "color": rust_data.get("color", 0),
        }
        
        # Convert FX data
        fx_raw = rust_data.get("fx", [])
        if fx_raw and len(fx_raw) > 0 and isinstance(fx_raw[0], int):
            # Parse FX data: first element is count, then FX info blocks
            fx_count = fx_raw[0]
            legacy_data["fx_count"] = fx_count
            legacy_data["fx"] = []
            
            pos = 1
            for fx_idx in range(fx_count):
                if pos >= len(fx_raw):
                    break
                    
                fx_info = {
                    "index": fx_idx,
                    "name": fx_raw[pos] if pos < len(fx_raw) else "Unknown",
                    "enabled": fx_raw[pos + 1] if pos + 1 < len(fx_raw) else True,
                    "preset": fx_raw[pos + 2] if pos + 2 < len(fx_raw) else "",
                    "param_count": fx_raw[pos + 3] if pos + 3 < len(fx_raw) else 0,
                    "params": []
                }
                pos += 4
                
                # Parse parameters
                param_count = fx_info["param_count"]
                if isinstance(param_count, int) and param_count > 0:
                    for param_idx in range(min(param_count, 20)):  # Limit to first 20 params like Rust code
                        if pos + 4 >= len(fx_raw):
                            break
                            
                        param_info = {
                            "index": param_idx,
                            "name": fx_raw[pos] if pos < len(fx_raw) else f"Param {param_idx}",
                            "value": fx_raw[pos + 1] if pos + 1 < len(fx_raw) else 0.0,
                            "min": fx_raw[pos + 2] if pos + 2 < len(fx_raw) else 0.0,
                            "max": fx_raw[pos + 3] if pos + 3 < len(fx_raw) else 1.0,
                            "formatted": fx_raw[pos + 4] if pos + 4 < len(fx_raw) else ""
                        }
                        fx_info["params"].append(param_info)
                        pos += 5
                
                legacy_data["fx"].append(fx_info)
        else:
            legacy_data["fx_count"] = 0
            legacy_data["fx"] = []
        
        # Convert send data
        send_raw = rust_data.get("sends", [])
        if send_raw and len(send_raw) > 0 and isinstance(send_raw[0], int):
            # Parse send data: first element is count, then send info blocks
            send_count = send_raw[0]
            legacy_data["send_count"] = send_count
            legacy_data["sends"] = []
            
            pos = 1
            for send_idx in range(send_count):
                if pos + 4 >= len(send_raw):
                    break
                    
                send_info = {
                    "index": send_idx,
                    "dest_name": send_raw[pos] if pos < len(send_raw) else "Unknown",
                    "dest_index": send_raw[pos + 1] if pos + 1 < len(send_raw) else -1,
                    "volume": send_raw[pos + 2] if pos + 2 < len(send_raw) else 1.0,
                    "pan": send_raw[pos + 3] if pos + 3 < len(send_raw) else 0.0,
                    "mute": send_raw[pos + 4] if pos + 4 < len(send_raw) else False,
                    # Note: Rust scan doesn't capture phase/mono, set defaults
                    "phase": False,
                    "mono": False
                }
                legacy_data["sends"].append(send_info)
                pos += 5
        else:
            legacy_data["send_count"] = 0
            legacy_data["sends"] = []
        
        return legacy_data
    
    def _populate_reafxs(self):
        """Create ReaFX objects from scan data."""
        if not self._scan_data or 'fx' not in self._scan_data:
            return
        
        from .fx import ReaFX
        
        for fx_data in self._scan_data['fx']:
            fx_index = fx_data['index']
            fx_name = fx_data['name']
            
            # Create ReaFX object with scan data
            fx_obj = ReaFX(
                client=self._client,
                track_index=self._index,
                fx_index=fx_index,
                name=fx_name,
                scan_data=fx_data,
                track_ref=self
            )
            
            # Store by index and snake_case name in cache
            self.reafxs[fx_index] = fx_obj
            snake_name = self._make_snake_name(fx_name)
            self.reafxs[snake_name] = fx_obj
    
    def _make_snake_name(self, name: str) -> str:
        """Convert a name to snake_case."""
        # Remove common prefixes and suffixes
        name = re.sub(r'^(VST3?i?:?\s*|AU:?\s*|JS:?\s*|VST:?\s*)', '', name)
        name = re.sub(r'\s*\([^)]*\)\s*$', '', name)  # Remove trailing parentheses
        
        # Convert to snake_case
        name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)  # camelCase to snake_case
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)  # Replace special chars with _
        name = re.sub(r'_+', '_', name)  # Collapse multiple underscores
        name = name.strip('_').lower()  # Remove leading/trailing _ and lowercase
        
        return name or 'unnamed'
    
    @property
    def index(self) -> int:
        """Get track index."""
        return self._index
    
    @property
    def id(self):
        """Get track ID (MediaTrack pointer)."""
        # Don't cache the track ID since it's now a pointer ID that's managed by Lua script
        return self._client.call_reascript_function("GetTrack", self._project.index, self._index)
    
    @property 
    def name(self) -> str:
        """Get track name via Rust OSC extension."""
        from ..tools.rust_osc_client import get_rust_osc_client
        rust_client = get_rust_osc_client()
        track_name = rust_client.get_track_name(self._index, timeout=1.0)
        return track_name or f"Track {self._index + 1}"
    
    @name.setter
    def name(self, value: str) -> None:
        """Set track name via Rust OSC extension."""
        from ..tools.rust_osc_client import get_rust_osc_client
        rust_client = get_rust_osc_client()
        if rust_client.set_track_name(self._index, value, timeout=2.0):
            logger.debug(f"Set track {self._index} name to: {value} via Rust OSC")
        else:
            logger.warning(f"Rust OSC extension failed to set track {self._index} name: {value}")
    
    @property
    def is_selected(self) -> bool:
        """Check if track is selected."""
        return bool(self._client.call_reascript_function("GetMediaTrackInfo_Value", self.id, "I_SELECTED"))
    
    @is_selected.setter
    def is_selected(self, value: bool) -> None:
        """Set track selection state."""
        self._client.call_reascript_function("SetTrackSelected", self.id, value)
    
    @property
    def is_muted(self) -> bool:
        """Check if track is muted."""
        return bool(self._client.call_reascript_function("GetMediaTrackInfo_Value", self.id, "B_MUTE"))
    
    @is_muted.setter
    def is_muted(self, value: bool) -> None:
        """Set track mute state."""
        # Use client with OSC if available
        self._client.set_track_mute(self._index + 1, value)  # Convert to 1-based
    
    @property
    def is_soloed(self) -> bool:
        """Check if track is soloed."""
        return bool(self._client.call_reascript_function("GetMediaTrackInfo_Value", self.id, "I_SOLO"))
    
    @is_soloed.setter
    def is_soloed(self, value: bool) -> None:
        """Set track solo state."""
        # Use client with OSC if available
        self._client.set_track_solo(self._index + 1, value)  # Convert to 1-based
    
    @property
    def is_armed(self) -> bool:
        """Check if track is record armed."""
        return bool(self._client.call_reascript_function("GetMediaTrackInfo_Value", self.id, "I_RECARM"))
    
    @is_armed.setter
    def is_armed(self, value: bool) -> None:
        """Set track record arm state."""
        self._client.call_reascript_function("SetMediaTrackInfo_Value", self.id, "I_RECARM", 1 if value else 0)
    
    @property
    def volume(self) -> float:
        """Get track volume."""
        return self._client.call_reascript_function("GetMediaTrackInfo_Value", self.id, "D_VOL")
    
    @volume.setter
    def volume(self, value: float) -> None:
        """Set track volume via REAPER OSC."""
        # Use REAPER's OSC interface directly (1-based track indexing)
        osc_address = f"/track/{self._index + 1}/volume"
        if self._client.send_osc_message(osc_address, value):
            logger.debug(f"Set track {self._index} volume to {value} via REAPER OSC")
        else:
            logger.warning(f"Failed to set track {self._index} volume via OSC")
    
    @property
    def pan(self) -> float:
        """Get track pan."""
        return self._client.call_reascript_function("GetMediaTrackInfo_Value", self.id, "D_PAN")
    
    @pan.setter
    def pan(self, value: float) -> None:
        """Set track pan via REAPER OSC."""
        # Use REAPER's OSC interface directly (1-based track indexing)
        osc_address = f"/track/{self._index + 1}/pan"
        if self._client.send_osc_message(osc_address, value):
            logger.debug(f"Set track {self._index} pan to {value} via REAPER OSC")
        else:
            logger.warning(f"Failed to set track {self._index} pan via OSC")
    
    @property
    def midi_channel(self) -> Optional[int]:
        """Get MIDI channel for this track (1-16), or None if not a MIDI track."""
        try:
            midi_input = self._client.call_reascript_function("GetMediaTrackInfo_Value", self.id, "I_RECINPUT")
            midi_input = int(midi_input)
            
            # Check if it's a MIDI track (has MIDI input configured)
            if midi_input >= 4096:
                # Extract MIDI channel from the input value
                # Low 5 bits are the channel (0=all, 1-16=specific)
                midi_channel = midi_input & 0x1F
                if 1 <= midi_channel <= 16:
                    return midi_channel
            return None
        except Exception as e:
            logger.warning(f"Failed to get MIDI channel for track {self._index}: {e}")
            return None
    
    def play_note(self, midi_note: int, velocity: int = 100, duration_ms: int = 1000) -> bool:
        """Play a MIDI note on this track with automatic note-off.
        
        Args:
            midi_note: MIDI note number (0-127)
            velocity: Note velocity (0-127) 
            duration_ms: Note duration in milliseconds
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If track is not configured for MIDI
        """
        channel = self.midi_channel
        if channel is None:
            raise ValueError(f"Track '{self.name}' is not configured for MIDI input")
        
        from ..tools.rust_osc_client import get_rust_osc_client
        rust_client = get_rust_osc_client()
        success = rust_client.play_note(channel, midi_note, velocity, duration_ms, timeout=2.0)
        if success:
            logger.debug(f"Played note {midi_note} on track '{self.name}' (ch{channel}) via Rust OSC")
        else:
            logger.warning(f"Failed to play note {midi_note} on track '{self.name}' via Rust OSC")
        return success
    
    @property
    def items(self) -> List:
        """Get list of all items on this track."""
        from .item import ReaItem
        
        items = []
        count = self._client.call_reascript_function("GetTrackNumMediaItems", self.id)
        
        for i in range(count):
            if i not in self._items:
                self._items[i] = ReaItem(self, i)
                
            items.append(self._items[i])
            
        return items
    
    def get_item(self, index: int):
        """Get item by index."""
        from .item import ReaItem
        
        # Check if item exists
        count = self._client.call_reascript_function("GetTrackNumMediaItems", self.id)
        if index < 0 or index >= count:
            raise ValueError(f"Item with index {index} doesn't exist on this track.")
        
        # Check cache and create Item object if needed
        if index not in self._items:
            self._items[index] = ReaItem(self, index)
            
        return self._items[index]
    
    def add_item(self, position: float = 0.0, length: float = 1.0):
        """Add a new item to the track."""
        from .item import ReaItem
        
        # Create new item
        self.is_selected = True  # Select this track
        self._reaper.perform_action(40142)  # Insert empty item
        
        # Get the new item (it will be the last one)
        count = self._client.call_reascript_function("GetTrackNumMediaItems", self.id)
        item_index = count - 1
        
        # Create Item object
        self._items[item_index] = ReaItem(self, item_index)
        
        # Set position and length
        item = self._items[item_index]
        item.position = position
        item.length = length
        
        return item
    
    def add_midi_item(self, position: float = 0.0, length: float = 1.0):
        """Add a new MIDI item to the track."""
        from .item import ReaItem
        
        # Create new MIDI item
        self.is_selected = True  # Select this track
        self._reaper.perform_action(40214)  # Insert empty MIDI item
        
        # Get the new item (it will be the last one)
        count = self._client.call_reascript_function("GetTrackNumMediaItems", self.id)
        item_index = count - 1
        
        # Create Item object
        self._items[item_index] = ReaItem(self, item_index)
        
        # Set position and length
        item = self._items[item_index]
        item.position = position
        item.length = length
        
        return item
    
    def add_audio_item(self, file_path: str, position: float = 0.0):
        """Add a new audio item to the track."""
        from .item import ReaItem
        
        # Create new audio item
        self.is_selected = True  # Select this track
        
        # Insert media file
        item_id = self._client.call_reascript_function("InsertMedia", file_path, 0)
        
        if not item_id:
            raise RuntimeError(f"Failed to insert audio file: {file_path}")
        
        # Get the new item (it will be the last one)
        count = self._client.call_reascript_function("GetTrackNumMediaItems", self.id)
        item_index = count - 1
        
        # Create Item object
        self._items[item_index] = ReaItem(self, item_index)
        
        # Set position
        item = self._items[item_index]
        item.position = position
        
        return item
    
    def delete(self) -> bool:
        """Delete this track."""
        self.is_selected = True
        return self._reaper.perform_action(40005)  # Delete track
        
    def add_chunk_to_track(self, chunk: str) -> bool:
        """Add a chunk to the track."""
        logger.debug(f"Adding chunk to track {self.index}")
        
        # Using a script-based approach to avoid MediaTrack issues
        add_chunk_script = f"""
        local track = reaper.GetTrack(0, {self._index})
        if not track then
            reaper.SetExtState("reaside", "chunk_result", "ERROR:TRACK_NOT_FOUND", false)
            return
        end
        
        local chunk = [=[{chunk}]=]
        local result = reaper.SetTrackStateChunk(track, chunk, false)
        reaper.SetExtState("reaside", "chunk_result", tostring(result), false)
        """
        
        # Execute the script
        self._client.set_ext_state("reaside", "temp_script", add_chunk_script)
        self._reaper.perform_action(65535)  # Run ReaScript: ReaScript_Runner
        
        # Get the result
        import time
        time.sleep(0.1)
        result_str = self._client.get_ext_state("reaside", "chunk_result")
        
        if result_str == "ERROR:TRACK_NOT_FOUND":
            raise ValueError(f"Track not found at index {self._index}")
            
        return result_str == "true" or result_str == "1"
    
    def add_fxchain(self, chain_path_or_name: Union[str, Path]) -> int:
        """Add an FX chain to the track using reaside server."""
        chain_path = None
        
        # Convert to Path object if string represents an existing file path
        if isinstance(chain_path_or_name, str):
            # Check if it's a direct file path
            potential_path = Path(chain_path_or_name)
            if potential_path.exists() and potential_path.suffix.lower() == '.rfxchain':
                chain_path = potential_path
            else:
                # Try to find the chain by name
                from .reaper import Reaper
                reaper = Reaper(self._client)
                chain_path = reaper.find_fxchain(chain_path_or_name)
        elif isinstance(chain_path_or_name, Path):
            chain_path = chain_path_or_name if chain_path_or_name.exists() else None
        
        # Check if we found a valid path
        if chain_path is None:
            raise FileNotFoundError(f"FX chain not found: {chain_path_or_name}")
        
        # Create request for the reaside server
        request = {
            "track_index": self._index,
            "file_path": str(chain_path)
        }
        
        # Send request to reaside server
        self._client.set_ext_state("reaside", "add_fxchain_request", request)
        
        # Wait for the server to process the request
        import time
        time.sleep(0.3)
        
        # Get the result
        result = self._client.get_ext_state("reaside", "add_fxchain_result")
        
        if isinstance(result, dict):
            if result.get("success"):
                fx_added = result.get("fx_added", 0)
                temp_fx_count = result.get("temp_fx_count", 0)
                moved_fx_count = result.get("moved_fx_count", 0)
                
                logger.info(f"Added FX chain '{chain_path.name}' to track {self._index} - {fx_added} FX added")
                logger.debug(f"Temp track had {temp_fx_count} FX, moved {moved_fx_count} FX")
                
                # Rescan track to update FX objects if FX were added
                if fx_added > 0:
                    self._scan_track()
                
                return fx_added
            elif result.get("error"):
                error_msg = result["error"]
                if error_msg == "Track not found":
                    raise RuntimeError(f"Track not found at index {self._index}")
                elif error_msg == "Failed to read FX chain file":
                    raise FileNotFoundError(f"Could not read FX chain file: {chain_path}")
                elif error_msg == "Invalid FX chain file format":
                    raise RuntimeError(f"Invalid FX chain file format: {chain_path}")
                elif error_msg == "Failed to create temporary track":
                    raise RuntimeError("Failed to create temporary track for FX chain loading")
                elif error_msg == "Failed to add chunk to temporary track":
                    raise RuntimeError("Failed to add FX chain chunk to temporary track")
                else:
                    raise RuntimeError(f"Error adding FX chain: {error_msg}")
        
        # If we get here, something went wrong
        raise RuntimeError(f"Unknown error adding FX chain: {result}")
        
    # Add alias for backward compatibility
    add_fx_chain = add_fxchain
    
    def add_fx(self, fx_name: str) -> bool:
        """Add a single FX to the track."""
        try:
            # Use TrackFX_AddByName to add the FX
            fx_index = self._client.call_reascript_function("TrackFX_AddByName", self.id, fx_name, False, -1)
            if fx_index >= 0:
                logger.info(f"Added FX '{fx_name}' to track {self._index + 1} at index {fx_index}")
                # Rescan track to update FX objects
                self._scan_track()
                return True
            else:
                logger.warning(f"Failed to add FX '{fx_name}' to track {self._index + 1}")
                return False
        except Exception as e:
            logger.error(f"Error adding FX '{fx_name}': {e}")
            return False
    
    # FX methods
    
    def get_fx_count(self) -> int:
        """Get the number of FX on this track."""
        return self._client.call_reascript_function("TrackFX_GetCount", self.id)
    
    def get_fx_name(self, fx_index: int) -> str:
        """Get the name of an FX at the given index."""
        result = self._client.call_reascript_function("TrackFX_GetFXName", self.id, fx_index, "", 256)
        if isinstance(result, tuple) and len(result) >= 2:
            return result[1]
        return result or ""
    
    def is_fx_enabled(self, fx_index: int) -> bool:
        """Check if an FX is enabled."""
        return self._client.call_reascript_function("TrackFX_GetEnabled", self.id, fx_index)
    
    def save_fxchain(self, chain_path: Union[str, Path]) -> bool:
        """Save current FX chain to a file using reaside server."""
        chain_path = Path(chain_path)
        
        # Ensure the directory exists
        chain_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create request for the reaside server
        request = {
            "track_index": self._index,
            "file_path": str(chain_path)
        }
        
        # Send request to reaside server
        self._client.set_ext_state("reaside", "save_fxchain_request", request)
        
        # Wait for the server to process the request
        import time
        time.sleep(0.2)
        
        # Get the result
        result = self._client.get_ext_state("reaside", "save_fxchain_result")
        
        if isinstance(result, dict):
            if result.get("success"):
                logger.info(f"FX chain saved to {chain_path}")
                return True
            elif result.get("error"):
                error_msg = result["error"]
                if error_msg == "Track not found":
                    raise ValueError(f"Track not found at index {self._index}")
                elif error_msg == "No FX on track":
                    raise ValueError("No FX on track to save")
                elif error_msg == "Failed to get track chunk":
                    raise RuntimeError("Failed to get track state chunk")
                elif error_msg == "Failed to write file":
                    raise RuntimeError(f"Failed to write to file {chain_path}")
                else:
                    raise RuntimeError(f"Error saving FX chain: {error_msg}")
        
        # If we get here, something went wrong
        raise RuntimeError(f"Unknown error saving FX chain: {result}")
    
    def load_fxchain(self, chain_path: Union[str, Path]) -> bool:
        """Load FX chain from a file."""
        chain_path = Path(chain_path)
        
        if not chain_path.exists():
            raise FileNotFoundError(f"FX chain file not found: {chain_path}")
        
        # Use the existing add_fxchain method
        try:
            fx_added = self.add_fxchain(chain_path)
            return fx_added > 0
        except Exception as e:
            logger.error(f"Failed to load FX chain: {e}")
            return False
    
    # Add aliases for backward compatibility
    save_fx_chain = save_fxchain
    load_fx_chain = load_fxchain
    
    # FX object access methods
    def get_fx(self, fx_identifier: Union[int, str]) -> Optional['ReaFX']:
        """Get ReaFX object by index or snake_case name."""
        return self.reafxs.get(fx_identifier)
    
    def get_fx_by_name(self, name: str) -> Optional['ReaFX']:
        """Get ReaFX object by original name or snake_case name."""
        # Try snake_case first
        snake_name = self._make_snake_name(name)
        fx = self.reafxs.get(snake_name)
        if fx:
            return fx
        
        # Try exact match with original name
        for fx in self.reafxs.values():
            if hasattr(fx, 'name') and fx.name == name:
                return fx
        
        return None
    
    def list_fx(self) -> List['ReaFX']:
        """Get list of all ReaFX objects on this track."""
        # Return only indexed FX objects (not the string keys)
        return [fx for key, fx in self.reafxs.items() if isinstance(key, int)]
    
    def rescan_fx(self):
        """Manually trigger FX rescan."""
        self._scan_track()
    
    def create_reafxs_for_chain(self, chain_name, param_alias_dict={}, scan_all_params=False):
        """
        Create ReaFX instances for a given FX chain.
        
        This method provides compatibility with the old ReaperIntegrationLib API.
        
        Args:
            chain_name: Name of the FX chain to add
            param_alias_dict: Dictionary of parameter aliases (not used in reaside)
            scan_all_params: Whether to scan all parameters (always True in reaside)
            
        Returns:
            List[str]: List of snake_case FX names that were created
        """
        # Get current FX count before adding chain
        fx_count_before = len(self.list_fx())
        
        # Add the FX chain
        fx_count_added = self.add_fxchain(chain_name)
        
        # Get the new FX objects (they were automatically scanned)
        all_fx = self.list_fx()
        new_fx_list = all_fx[fx_count_before:fx_count_before + fx_count_added]
        
        # Return the snake_case names of the new FX
        chain_reafx_names = []
        for fx in new_fx_list:
            # The FX name is already snake_case in reaside
            snake_name = fx.snake_name
            chain_reafx_names.append(snake_name)
            
        return chain_reafx_names
    
    def __getattr__(self, name: str):
        """Allow accessing FX and sends by snake_case name as attributes."""
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        # Check for FX first
        fx = self.reafxs.get(name)
        if fx:
            return fx
        
        # Check for sends
        send = self.sends.get(name)
        if send:
            return send
        
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def add_send(self, destination_track, volume: float = 0.0, pan: float = 0.0, 
                 mute: bool = False, mode: str = "post_fx"):
        """
        Add a send from this track to another track (typically a bus).
        Will not create a duplicate send if one already exists to the same destination.
        
        Args:
            destination_track: The destination ReaTrack, track index, or track name to send to
            volume: Send volume (0.0 to 1.0, default 0.0)
            pan: Send pan (-1.0 to 1.0, default 0.0 center)
            mute: Whether the send should be muted (default False)
            mode: Send mode - "pre_fx" (pre-fader pre-fx), "post_fx" (pre-fader post-fx), "post_fader" (post-fader pre-fx) (default "post_fx")
            
        Returns:
            int: The send index that was created, or -1 if failed
        """
        try:
            # Get destination track index
            if hasattr(destination_track, '_index'):  # Check for ReaTrack object
                dest_track_index = destination_track.index
                dest_name = destination_track.name if hasattr(destination_track, 'name') else f"Track {dest_track_index + 1}"
            elif isinstance(destination_track, int):
                dest_track_index = destination_track
                dest_name = f"Track {dest_track_index + 1}"
            elif isinstance(destination_track, str):
                # Look for track by name
                dest_track = self._project.get_track_by_name(destination_track)
                if dest_track:
                    dest_track_index = dest_track.index
                    dest_name = destination_track
                else:
                    logger.error(f"Track with name '{destination_track}' not found")
                    return -1
            else:
                logger.error(f"Invalid destination track: {destination_track}")
                return -1
            
            # Get MediaTrack objects
            source_track_obj = self._client.call_reascript_function("GetTrack", 0, self._index)
            dest_track_obj = self._client.call_reascript_function("GetTrack", 0, dest_track_index)
            
            if not source_track_obj or not dest_track_obj:
                logger.error(f"Failed to get track objects for send creation")
                return -1
            
            # Check if a send to this destination already exists
            num_sends = self._client.call_reascript_function("GetTrackNumSends", source_track_obj, 0)
            for send_idx in range(num_sends):
                existing_dest = self._client.call_reascript_function("GetTrackSendInfo_Value", source_track_obj, 0, send_idx, "P_DESTTRACK")
                if existing_dest == dest_track_obj:
                    logger.info(f"Send from '{self.name}' to '{dest_name}' already exists (index {send_idx})")
                    
                    # Create ReaSend instance for existing send if not already present
                    dest_snake_name = self._make_snake_name(dest_name)
                    if dest_snake_name not in self.sends:
                        from .param import ReaSend
                        
                        # Create dB-based volume control
                        send_volume_db = ReaSend(
                            client=self._client,
                            track_index=self._index,
                            send_index=send_idx,
                            param_type="volume_db",
                            name=f"{dest_name}"
                        )
                        
                        # Create linear volume control
                        send_volume_lin = ReaSend(
                            client=self._client,
                            track_index=self._index,
                            send_index=send_idx,
                            param_type="volume_lin",
                            name=f"{dest_name}_lin"
                        )
                        
                        # Store both versions
                        self.sends[dest_snake_name] = send_volume_db
                        self.sends[f"{dest_snake_name}_lin"] = send_volume_lin
                    
                    return send_idx
            
            # Convert mode string to REAPER send mode index
            # Based on REAPER behavior: 
            # 0 = pre_fader pre_fx, 1 = post_fader pre_fx, 3 = pre_fader post_fx
            if mode == "pre_fx":
                mode_idx = 0  # pre_fader pre_fx
            elif mode == "post_fx":
                mode_idx = 3  # pre_fader post_fx  
            elif mode == "post_fader":
                mode_idx = 1  # post_fader pre_fx
            else:
                raise ValueError(f"Invalid send mode '{mode}'. Choose between 'pre_fx', 'post_fx', or 'post_fader'")
            
            # Create the send using CreateTrackSend
            send_index = self._client.call_reascript_function("CreateTrackSend", source_track_obj, dest_track_obj)
            
            if send_index < 0:
                logger.error(f"Failed to create send from track {self._index} to track {dest_track_index}")
                return -1
            
            # Configure send parameters
            # Set send volume
            self._client.call_reascript_function("SetTrackSendInfo_Value", source_track_obj, 0, send_index, "D_VOL", volume)
            
            # Set send pan
            self._client.call_reascript_function("SetTrackSendInfo_Value", source_track_obj, 0, send_index, "D_PAN", pan)
            
            # Set send mute
            self._client.call_reascript_function("SetTrackSendInfo_Value", source_track_obj, 0, send_index, "B_MUTE", 1 if mute else 0)
            
            # Set send mode
            self._client.call_reascript_function("SetTrackSendInfo_Value", source_track_obj, 0, send_index, "I_SENDMODE", mode_idx)
            
            # Create ReaSend instance for volume control
            from .param import ReaSend
            
            # Create ReaSend for dB-based volume control with the destination track name
            send_volume_db = ReaSend(
                client=self._client,
                track_index=self._index,
                send_index=send_index,
                param_type="volume_db",
                name=f"{dest_name}"
            )
            
            # Create ReaSend for linear volume control
            send_volume_lin = ReaSend(
                client=self._client,
                track_index=self._index,
                send_index=send_index,
                param_type="volume_lin",
                name=f"{dest_name}_lin"
            )
            
            # Store the sends by destination track name (make it snake_case for consistency)
            dest_snake_name = self._make_snake_name(dest_name)
            
            # Store dB version (default)
            self.sends[dest_snake_name] = send_volume_db
            
            # Store linear version with _lin suffix
            self.sends[f"{dest_snake_name}_lin"] = send_volume_lin
            
            logger.info(f"Created send from '{self.name}' to '{dest_name}' (index {send_index})")
            
            return send_index
            
        except Exception as e:
            logger.error(f"Error creating send from track {self._index}: {e}")
            return -1
    
    def remove_send(self, send_index: int) -> bool:
        """
        Remove a send by its index.
        
        Args:
            send_index: Index of the send to remove
            
        Returns:
            bool: True if successful, False if failed
        """
        try:
            track_obj = self._client.call_reascript_function("GetTrack", 0, self._index)
            if not track_obj:
                logger.error(f"Failed to get track object for send removal")
                return False
            
            # Remove the send using RemoveTrackSend
            result = self._client.call_reascript_function("RemoveTrackSend", track_obj, 0, send_index)
            
            if result:
                logger.info(f"Removed send {send_index} from track '{self.name}'")
                return True
            else:
                logger.warning(f"Failed to remove send {send_index} from track '{self.name}'")
                return False
                
        except Exception as e:
            logger.error(f"Error removing send {send_index} from track {self._index}: {e}")
            return False
    
    def get_send_count(self) -> int:
        """
        Get the number of sends on this track.
        
        Returns:
            int: Number of sends
        """
        try:
            track_obj = self._client.call_reascript_function("GetTrack", 0, self._index)
            if track_obj:
                return self._client.call_reascript_function("GetTrackNumSends", track_obj, 0)
            return 0
        except Exception as e:
            logger.error(f"Error getting send count for track {self._index}: {e}")
            return 0