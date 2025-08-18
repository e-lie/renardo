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
        
        # Perform initial scan to populate FX and parameters
        self._scan_track()
        
    def _scan_track(self):
        """Scan track to populate FX and parameter information."""
        try:
            scan_result = self._client.scan_track_complete(self._index)
            if scan_result and scan_result.get('success'):
                self._scan_data = scan_result['track']
                self._populate_reafxs()
        except Exception as e:
            logger.warning(f"Failed to scan track {self._index}: {e}")
            self._scan_data = None
    
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
                scan_data=fx_data
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
        """Get track name."""
        # GetTrackName returns (retval, name)
        result = self._client.call_reascript_function("GetTrackName", self.id, "", 1024)
        if isinstance(result, tuple) and len(result) >= 2:
            return result[1]  # Return the track name
        elif isinstance(result, tuple) and len(result) == 1:
            return result[0] if result[0] else f"Track {self._index + 1}"
        else:
            return str(result) if result else f"Track {self._index + 1}"
    
    @name.setter
    def name(self, value: str) -> None:
        """Set track name."""
        self._client.call_reascript_function("GetSetMediaTrackInfo_String", self.id, "P_NAME", value, True)
    
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
        """Set track volume."""
        # Use unified client for better performance with OSC if available
        self._client.set_track_volume(self._index + 1, value)  # Convert to 1-based
    
    @property
    def pan(self) -> float:
        """Get track pan."""
        return self._client.call_reascript_function("GetMediaTrackInfo_Value", self.id, "D_PAN")
    
    @pan.setter
    def pan(self, value: float) -> None:
        """Set track pan."""
        # Use unified client for better performance with OSC if available
        self._client.set_track_pan(self._index + 1, value)  # Convert to 1-based
    
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
        """Allow accessing FX by snake_case name as attributes."""
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        fx = self.reafxs.get(name)
        if fx:
            return fx
        
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def add_send_to_track(self, destination_track, volume: float = 1.0, pan: float = 0.0, 
                         mute: bool = False, post_fader: bool = True):
        """
        Add a send from this track to another track (typically a bus).
        
        Args:
            destination_track: The destination ReaTrack or track index to send to
            volume: Send volume (0.0 to 1.0, default 1.0)
            pan: Send pan (-1.0 to 1.0, default 0.0 center)
            mute: Whether the send should be muted (default False)
            post_fader: True for post-fader send, False for pre-fader (default True)
            
        Returns:
            int: The send index that was created, or -1 if failed
        """
        try:
            # Get destination track index
            if hasattr(destination_track, 'index'):
                dest_track_index = destination_track.index
            elif isinstance(destination_track, int):
                dest_track_index = destination_track
            else:
                logger.error(f"Invalid destination track: {destination_track}")
                return -1
            
            # Get MediaTrack objects
            source_track_obj = self._client.call_reascript_function("GetTrack", 0, self._index)
            dest_track_obj = self._client.call_reascript_function("GetTrack", 0, dest_track_index)
            
            if not source_track_obj or not dest_track_obj:
                logger.error(f"Failed to get track objects for send creation")
                return -1
            
            # Create the send using CreateTrackSend
            # Args: source_track, dest_track, send_type (0=post-fader, 1=pre-fader)
            send_type = 0 if post_fader else 1
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
            
            # Set send mode (post/pre fader)
            self._client.call_reascript_function("SetTrackSendInfo_Value", source_track_obj, 0, send_index, "I_SENDMODE", send_type)
            
            dest_name = destination_track.name if hasattr(destination_track, 'name') else f"Track {dest_track_index + 1}"
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