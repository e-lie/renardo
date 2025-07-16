"""Track-related functionality module."""

import logging
import os
import re
from pathlib import Path
from typing import Optional, List, Union, Dict, Any

logger = logging.getLogger(__name__)

class ReaTrack:
    """REAPER track."""
    
    def __init__(self, project, index):
        """Initialize the Track object."""
        self._project = project
        self._reaper = project._reaper
        self._client = project._client
        self._index = index
        self._items = {}  # Cache for Item objects
        self._fx_objects = {}  # Cache for ReaFX objects
        self._scan_data = None  # Track scan data cache
        
        # Perform initial scan to populate FX and parameters
        self._scan_track()
        
    def _scan_track(self):
        """Scan track to populate FX and parameter information."""
        try:
            scan_result = self._client.scan_track_complete(self._index)
            if scan_result and scan_result.get('success'):
                self._scan_data = scan_result['track']
                self._populate_fx_objects()
        except Exception as e:
            logger.warning(f"Failed to scan track {self._index}: {e}")
            self._scan_data = None
    
    def _populate_fx_objects(self):
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
            
            # Store by index and snake_case name
            self._fx_objects[fx_index] = fx_obj
            snake_name = self._make_snake_name(fx_name)
            self._fx_objects[snake_name] = fx_obj
    
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
        # Use unified client for better performance with OSC if available
        self._client.set_track_mute(self._index + 1, value)  # Convert to 1-based
    
    @property
    def is_soloed(self) -> bool:
        """Check if track is soloed."""
        return bool(self._client.call_reascript_function("GetMediaTrackInfo_Value", self.id, "I_SOLO"))
    
    @is_soloed.setter
    def is_soloed(self, value: bool) -> None:
        """Set track solo state."""
        # Use unified client for better performance with OSC if available
        self._client.set_track_solo(self._index + 1, value)  # Convert to 1-based
    
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
        """Add an FX chain to the track."""
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
        
        # Make sure chain_path is a string
        chain_path_str = str(chain_path)
        
        # Use a completely script-based approach to avoid MediaTrack issues
        # Store the track index and FX chain path
        self._client.set_ext_state("reaside", "track_index", str(self._index))
        self._client.set_ext_state("reaside", "fxchain_path", chain_path_str)
        
        # Create a comprehensive script that handles everything
        full_script = f"""
        -- Get our track
        local track_index = {self._index}
        local track = reaper.GetTrack(0, track_index)
        if not track then
            reaper.SetExtState("reaside", "fxchain_result", "ERROR:TRACK_NOT_FOUND", false)
            return
        end
        
        -- Get FX count before adding the chain
        local fx_count_before = reaper.TrackFX_GetCount(track)
        
        -- Select just this track (required for some operations)
        reaper.Main_OnCommand(40297, 0) -- Track: Unselect all tracks
        reaper.SetTrackSelected(track, true)
        
        -- Get the FX chain path
        local chain_path = "{chain_path_str.replace('\\', '\\\\')}"
        local success = 0
        
        -- Method 1: Try direct API
        local result1 = reaper.TrackFX_AddByName(track, chain_path, false, -1)
        if result1 >= 0 then
            success = 1
        else
            -- Method 2: Try with track state chunk
            local retval, chunk = reaper.GetTrackStateChunk(track, "", 16384, false)
            if retval then
                local file = io.open(chain_path, "r")
                if file then
                    local chain_content = file:read("*all")
                    file:close()
                    
                    if chain_content:find("<FXCHAIN") then
                        -- Insert the FX chain content
                        if chunk:find("<FXCHAIN") then
                            local start = chunk:find("<FXCHAIN")
                            local end_pos = chunk:find(">", chunk:find("</FXCHAIN")) + 1
                            if end_pos > start then
                                chunk = chunk:sub(1, start) .. chain_content .. chunk:sub(end_pos)
                                if reaper.SetTrackStateChunk(track, chunk, false) then
                                    success = 2
                                end
                            end
                        else
                            -- Add at the end
                            chunk = chunk:sub(1, -2) .. "\\n" .. chain_content .. "\\n>"
                            if reaper.SetTrackStateChunk(track, chunk, false) then
                                success = 2
                            end
                        end
                    end
                end
            end
            
            -- Method 3: Try another approach with the chain
            if success == 0 then
                -- Try loading the fx chain via action and command ID
                reaper.Main_OnCommand(41051, 0)  -- Track: Load FX chain
                -- Can't fully automate file dialog via script, but we tried!
                success = 3  -- Assume it might work
            end
        end
        
        -- Get FX count after adding the chain
        local fx_count_after = reaper.TrackFX_GetCount(track)
        
        -- Store the results
        reaper.SetExtState("reaside", "fx_count_before", tostring(fx_count_before), false)
        reaper.SetExtState("reaside", "fx_count_after", tostring(fx_count_after), false)
        reaper.SetExtState("reaside", "fxchain_method", tostring(success), false)
        """
        
        # Execute the script in REAPER
        self._client.set_ext_state("reaside", "temp_script", full_script)
        self._reaper.perform_action(65535)  # Run ReaScript: ReaScript_Runner
        
        # Give REAPER time to process
        import time
        time.sleep(0.3)
        
        # Retrieve the results
        fx_count_before_str = self._client.get_ext_state("reaside", "fx_count_before")
        fx_count_after_str = self._client.get_ext_state("reaside", "fx_count_after")
        method = self._client.get_ext_state("reaside", "fxchain_method")
        
        # Check for errors
        result = self._client.get_ext_state("reaside", "fxchain_result")
        if result and result.startswith("ERROR:"):
            raise RuntimeError(f"Failed to add FX chain: {result[6:]}")
        
        # Parse the counts
        try:
            fx_count_before = int(fx_count_before_str) if fx_count_before_str else 0
            fx_count_after = int(fx_count_after_str) if fx_count_after_str else 0
        except (ValueError, TypeError):
            logger.warning("Could not parse FX counts from REAPER")
            return 0
            
        # Log which method worked
        if method:
            logger.debug(f"FX chain added using method {method}")
            
        # Return how many FX were added
        fx_added = fx_count_after - fx_count_before
        
        # Rescan track to update FX objects if FX were added
        if fx_added > 0:
            self._scan_track()
        
        return fx_added
        
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
    
    # MIDI note methods
    def send_note_on(self, pitch: int, velocity: int = 100, channel: int = 0):
        """Send MIDI note on to this track."""
        return self._client.send_note_on(self._index + 1, pitch, velocity, channel)
    
    def send_note_off(self, pitch: int, channel: int = 0):
        """Send MIDI note off to this track."""
        return self._client.send_note_off(self._index + 1, pitch, channel)
    
    def send_all_notes_off(self):
        """Send all notes off to this track."""
        return self._client.send_all_notes_off(self._index + 1)
    
    def play_note(self, pitch: int, velocity: int = 100, duration: float = 0.5, channel: int = 0):
        """Play a note for a specific duration."""
        # Send note on
        self.send_note_on(pitch, velocity, channel)
        
        # Schedule note off (non-blocking)
        import threading
        def note_off_timer():
            import time
            time.sleep(duration)
            self.send_note_off(pitch, channel)
        
        timer = threading.Timer(duration, note_off_timer)
        timer.start()
        return timer
    
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
    
    def save_fx_chain(self, chain_path: Union[str, Path]) -> bool:
        """Save current FX chain to a file."""
        chain_path = Path(chain_path)
        
        # Ensure the directory exists
        chain_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use Lua script to save FX chain
        save_script = f"""
        local track = reaper.GetTrack(0, {self._index})
        if not track then
            reaper.SetExtState("reaside", "save_result", "ERROR:TRACK_NOT_FOUND", false)
            return
        end
        
        local fx_count = reaper.TrackFX_GetCount(track)
        if fx_count == 0 then
            reaper.SetExtState("reaside", "save_result", "ERROR:NO_FX", false)
            return
        end
        
        -- Get track state chunk
        local retval, chunk = reaper.GetTrackStateChunk(track, "", 16384, false)
        if not retval then
            reaper.SetExtState("reaside", "save_result", "ERROR:CHUNK_FAILED", false)
            return
        end
        
        -- Extract FX section from chunk
        local fx_section = ""
        local in_fx_section = false
        for line in chunk:gmatch("[^\\n]+") do
            if line:match("^<FXCHAIN") then
                in_fx_section = true
                fx_section = fx_section .. line .. "\\n"
            elseif line:match("^>") and in_fx_section then
                fx_section = fx_section .. line .. "\\n"
                break
            elseif in_fx_section then
                fx_section = fx_section .. line .. "\\n"
            end
        end
        
        -- Write to file
        local file = io.open("{str(chain_path).replace('\\', '\\\\')}", "w")
        if file then
            file:write(fx_section)
            file:close()
            reaper.SetExtState("reaside", "save_result", "SUCCESS", false)
        else
            reaper.SetExtState("reaside", "save_result", "ERROR:FILE_WRITE", false)
        end
        """
        
        # Execute the script
        self._client.set_ext_state("reaside", "temp_script", save_script)
        self._reaper.perform_action(65535)  # Run ReaScript
        
        # Check result
        import time
        time.sleep(0.1)
        result = self._client.get_ext_state("reaside", "save_result")
        
        if result == "SUCCESS":
            logger.info(f"FX chain saved to {chain_path}")
            return True
        elif result == "ERROR:TRACK_NOT_FOUND":
            raise ValueError(f"Track not found at index {self._index}")
        elif result == "ERROR:NO_FX":
            raise ValueError("No FX on track to save")
        elif result == "ERROR:CHUNK_FAILED":
            raise RuntimeError("Failed to get track state chunk")
        elif result == "ERROR:FILE_WRITE":
            raise RuntimeError(f"Failed to write to file {chain_path}")
        else:
            raise RuntimeError(f"Unknown error saving FX chain: {result}")
    
    def load_fx_chain(self, chain_path: Union[str, Path]) -> bool:
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
    
    # FX object access methods
    def get_fx(self, fx_identifier: Union[int, str]) -> Optional['ReaFX']:
        """Get ReaFX object by index or snake_case name."""
        return self._fx_objects.get(fx_identifier)
    
    def get_fx_by_name(self, name: str) -> Optional['ReaFX']:
        """Get ReaFX object by original name or snake_case name."""
        # Try snake_case first
        snake_name = self._make_snake_name(name)
        fx = self._fx_objects.get(snake_name)
        if fx:
            return fx
        
        # Try exact match with original name
        for fx in self._fx_objects.values():
            if hasattr(fx, 'name') and fx.name == name:
                return fx
        
        return None
    
    def list_fx(self) -> List['ReaFX']:
        """Get list of all ReaFX objects on this track."""
        # Return only indexed FX objects (not the string keys)
        return [fx for key, fx in self._fx_objects.items() if isinstance(key, int)]
    
    def rescan_fx(self):
        """Manually trigger FX rescan."""
        self._scan_track()
    
    def __getattr__(self, name: str):
        """Allow accessing FX by snake_case name as attributes."""
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        fx = self._fx_objects.get(name)
        if fx:
            return fx
        
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")