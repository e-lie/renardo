"""Project-related functionality module."""

from renardo.logger import get_logger
from typing import Optional, List, Union, Dict, Any
from ..tools.rust_osc_client import get_rust_osc_client

logger = get_logger('reaside.core.project')

class ReaProject:
    """REAPER project."""
    
    def __init__(self, reaper, index):
        """Initialize the Project object."""
        self._reaper = reaper
        self._client = reaper._client
        self._index = index
        self.reatracks = {}  # Cache for Track objects (compatible with old API)
        self._bus_tracks: Dict[int, 'ReaTrack'] = {}  # Bus tracks by bus index
        self._instrument_tracks: Dict[int, 'ReaTrack'] = {}  # Instrument tracks by MIDI channel (1-16)
        
        # Automatically scan and populate all tracks
        self._scan_all_tracks()
        
    def _scan_all_tracks(self):
        """Scan all tracks in the project and populate ReaTrack instances."""
        try:
            # Get total track count
            track_count = self._client.call_reascript_function("CountTracks", self._index)
            
            if track_count > 0:
                logger.info(f"Scanning {track_count} tracks in project {self._index}")
                
                # Scan each track and populate ReaTrack instances
                for track_idx in range(track_count):
                    self._scan_and_populate_track(track_idx)
                    
                logger.info(f"Completed scanning {track_count} tracks")
            else:
                logger.debug("No tracks found in project")
                
        except Exception as e:
            logger.warning(f"Failed to scan tracks in project {self._index}: {e}")
    
    def _scan_and_populate_track(self, track_index: int):
        """Scan a single track and create ReaTrack instance."""
        try:
            from .track import ReaTrack
            
            # Create ReaTrack instance (this will automatically scan the track)
            track = ReaTrack(self, track_index)
            
            # Store in cache
            self.reatracks[track_index] = track
            
            # Categorize track based on its MIDI input configuration
            track_obj = self._client.call_reascript_function("GetTrack", 0, track_index)
            if track_obj:
                midi_input = self._client.call_reascript_function("GetMediaTrackInfo_Value", track_obj, "I_RECINPUT")
                
                # Convert to int for bitwise operations
                midi_input = int(midi_input)
                
                # Check if it's a MIDI track (has MIDI input configured)
                if midi_input >= 4096:
                    # Extract MIDI channel from the input value
                    # Low 5 bits are the channel (0=all, 1-16=specific)
                    midi_channel = midi_input & 0x1F
                    if 1 <= midi_channel <= 16:
                        # Store by MIDI channel
                        self._instrument_tracks[midi_channel] = track
                elif midi_input < 0:
                    # This is a bus track (no input)
                    # Find the next available bus index
                    bus_index = len(self._bus_tracks)
                    self._bus_tracks[bus_index] = track
            
            logger.debug(f"Created ReaTrack for track {track_index}: {track.name}")
            
        except Exception as e:
            logger.warning(f"Failed to scan track {track_index}: {e}")
    
    @property
    def index(self) -> int:
        """Get project index."""
        return self._index
    
    @property
    def name(self) -> str:
        """Get project name via Rust OSC extension."""
        try:
            rust_client = get_rust_osc_client()
            project_name = rust_client.get_project_name(timeout=1.0)
            return project_name or "Untitled"
        except Exception as e:
            logger.warning(f"Rust OSC extension not available: {e}")
            return "Untitled"
    
    @name.setter
    def name(self, value: str) -> None:
        """Set project name via Rust OSC extension."""
        try:
            rust_client = get_rust_osc_client()
            if rust_client.set_project_name(value, timeout=2.0):
                logger.debug(f"Set project name via Rust extension: {value}")
            else:
                logger.warning(f"Rust OSC extension failed to set project name: {value}")
        except Exception as e:
            logger.error(f"Rust OSC extension not available: {e}")
    
    def add_track_configured(self, position: int = -1, name: str = "", 
                           input_value: int = -1, record_armed: bool = False, record_mode: int = 2) -> Optional['ReaTrack']:
        """Add a new track via Rust OSC extension with configuration.
        
        Args:
            position: Where to insert track (-1 for end)
            name: Track name (empty string for default) 
            input_value: MIDI input value (-1 for no input, 0+ for MIDI channels)
            record_armed: Whether to arm track for recording
            record_mode: Record mode (0=output, 1=output stereo, 2=none/monitor input, 3=midi output)
            
        Returns:
            ReaTrack instance for the new track or None if failed
        """
        try:
            rust_client = get_rust_osc_client()
            track_index = rust_client.add_track(
                position=position, 
                name=name, 
                input_value=input_value, 
                record_armed=record_armed,
                record_mode=record_mode,
                timeout=2.0
            )
            if track_index is not None:
                logger.debug(f"Added configured track via Rust OSC at index: {track_index}")
                # Create ReaTrack instance for the new track
                from .track import ReaTrack
                new_track = ReaTrack(self, track_index)
                # Update our internal tracking
                self.reatracks[track_index] = new_track
                return new_track
            else:
                logger.warning("Rust OSC extension failed to add track")
                return None
        except Exception as e:
            logger.error(f"Rust OSC extension not available for adding track: {e}")
            return None
    
    @property
    def path(self) -> str:
        """Get project file path."""
        # GetProjectPath takes project, buf, buf_size
        path = self._client.call_reascript_function("GetProjectPath", self._index, "", 1024)
        return path
    
    @property
    def length(self) -> float:
        """Get project length in seconds."""
        return self._client.call_reascript_function("GetProjectLength", self._index)
    
    @property
    def bpm(self) -> float:
        """Get project tempo."""
        return self._client.call_reascript_function("GetProjectTimeSignature2", self._index, 0, 0)[0]
    
    @bpm.setter
    def bpm(self, value: float) -> None:
        """Set project tempo."""
        self._client.call_reascript_function("SetTempoTimeSigMarker", self._index, -1, 0, -1, -1, value, -1, -1, False)
    
    @property
    def time_signature(self) -> tuple:
        """Get project time signature."""
        _, num, denom = self._client.call_reascript_function("GetProjectTimeSignature2", self._index, 0, 0)
        return (num, denom)
    
    @time_signature.setter
    def time_signature(self, value: tuple) -> None:
        """Set project time signature."""
        num, denom = value
        self._client.call_reascript_function("SetTempoTimeSigMarker", self._index, -1, 0, -1, -1, -1, num, denom, False)
    
    @property
    def selected_tracks(self) -> List:
        """Get list of selected tracks."""
        from .track import ReaTrack
        
        tracks = []
        count = self._client.call_reascript_function("CountSelectedTracks", self._index)
        
        for i in range(count):
            track_id = self._client.call_reascript_function("GetSelectedTrack", self._index, i)
            track_index = self._client.call_reascript_function("GetMediaTrackInfo_Value", track_id, "IP_TRACKNUMBER")
            
            # Track indexes in REAPER are 1-based, but we convert to 0-based
            track_index = int(track_index) - 1
            
            if track_index not in self.reatracks:
                self.reatracks[track_index] = ReaTrack(self, track_index)
                
            tracks.append(self.reatracks[track_index])
            
        return tracks
    
    @property
    def tracks(self) -> List:
        """Get list of all tracks."""
        # Return tracks in index order
        return [self.reatracks[i] for i in sorted(self.reatracks.keys())]
    
    @property
    def bus_tracks(self) -> List:
        """Get list of bus tracks ordered by bus index."""
        return [self._bus_tracks[idx] for idx in sorted(self._bus_tracks.keys())]
    
    @property
    def instrument_tracks(self) -> List:
        """Get list of instrument tracks ordered by MIDI channel."""
        return [self._instrument_tracks[ch] for ch in sorted(self._instrument_tracks.keys())]
    
    def _is_bus_track(self, track) -> bool:
        """Check if a track is a bus track based on its properties."""
        try:
            # Get track's MIDI input configuration
            track_obj = self._client.call_reascript_function("GetTrack", 0, track._index)
            if track_obj:
                midi_input = self._client.call_reascript_function("GetMediaTrackInfo_Value", track_obj, "I_RECINPUT")
                # Bus tracks have no input (-1) or are not MIDI tracks (< 4096)
                return midi_input < 0 or (midi_input >= 0 and midi_input < 4096)
            return False
        except:
            return False
    
    def get_track(self, index: int):
        """Get track by index."""
        # Check if track exists in cache
        if index in self.reatracks:
            return self.reatracks[index]
        
        # Check if track exists in REAPER
        count = self._client.call_reascript_function("CountTracks", self._index)
        if index < 0 or index >= count:
            raise ValueError(f"Track with index {index} doesn't exist.")
        
        # Create new track (this will automatically scan it)
        self._scan_and_populate_track(index)
        return self.reatracks[index]
    
    def get_track_by_name(self, name: str, case_sensitive: bool = False):
        """Get track by name."""
        # Search in cached tracks first
        for track in self.reatracks.values():
            track_name = track.name
            
            if case_sensitive:
                match = track_name == name
            else:
                match = track_name.lower() == name.lower()
                
            if match:
                return track
                
        return None
    
    def add_track(self, position: Optional[int] = None, name: str = "", 
                  input_value: int = -1, record_armed: bool = False, record_mode: int = 2):
        """Add a new track to the project with optional configuration.
        
        Args:
            position: Track index where to insert (0-based). If None, adds at the end.
            name: Track name (empty string for default)
            input_value: MIDI input value (-1 for no input, 0+ for MIDI channels)  
            record_armed: Whether to arm track for recording
            record_mode: Record mode (0=output, 1=output stereo, 2=none/monitor input, 3=midi output)
            
        Returns:
            ReaTrack: The newly created track
        """
        # Convert None position to -1 for Rust extension
        pos = -1 if position is None else position
        
        try:
            # Try Rust OSC extension first
            new_track = self.add_track_configured(
                position=pos, 
                name=name, 
                input_value=input_value, 
                record_armed=record_armed,
                record_mode=record_mode
            )
            if new_track:
                return new_track
            
            logger.warning("Rust OSC extension failed, falling back to legacy method")
        except Exception as e:
            logger.warning(f"Rust OSC extension not available: {e}, using legacy method")
        
        # Fallback to legacy method (simplified - just basic track creation)
        if position is None:
            # Add at the end using action
            self._reaper.perform_action(40001)
            count = self._client.call_reascript_function("CountTracks", self._index)
            track_index = count - 1
        else:
            # Insert at specific position using InsertTrackAtIndex
            self._client.call_reascript_function("InsertTrackAtIndex", position, False)
            track_index = position
            
            # Update indices of existing tracks that were shifted
            for idx in sorted(self.reatracks.keys(), reverse=True):
                if idx >= position:
                    track = self.reatracks[idx]
                    track._index = idx + 1
                    del self.reatracks[idx]
                    self.reatracks[idx + 1] = track
        
        # Create and return Track object
        self._scan_and_populate_track(track_index)
        return self.reatracks[track_index]
    
    def save(self, file_path: Optional[str] = None) -> bool:
        """Save the project."""
        if file_path:
            return self._client.call_reascript_function("Main_SaveProjectEx", self._index, file_path, False)
        else:
            return self._client.call_reascript_function("Main_SaveProject", self._index, False)
    
    def close(self, save: bool = True) -> bool:
        """Close the project."""
        if save:
            self.save()
        
        return self._client.call_reascript_function("Main_OnCommand", 40860, 0)  # Close current project tab
    
    def rescan_all_tracks(self):
        """Manually trigger rescan of all tracks."""
        self.reatracks.clear()
        self._scan_all_tracks()
    
    @property
    def track_count(self) -> int:
        """Get the number of tracks in the project."""
        return len(self.reatracks)
    
    def list_tracks(self) -> List['ReaTrack']:
        """Get list of all tracks (same as tracks property)."""
        return self.tracks
    
    def __len__(self) -> int:
        """Get number of tracks."""
        return len(self.reatracks)
    
    def __getitem__(self, index: int) -> 'ReaTrack':
        """Get track by index using bracket notation."""
        return self.get_track(index)
    
    def __iter__(self):
        """Iterate over tracks."""
        return iter(self.tracks)
    
    def create_instrument_track(self, track_name: str, midi_channel: int):
        """
        Create an instrument track for renardo integration.

        The track is:
        - Named with the provided track_name
        - Record armed
        - Set to receive from "All MIDI inputs" on the specified MIDI channel
        - Record mode set to "Stereo Out" (monitors the track output)
        - Placed in order by MIDI channel
        
        Args:
            track_name: Name for the track
            midi_channel: MIDI channel number (1-16)
            
        Returns:
            ReaTrack: The created track
        """
        # Calculate the position: after bus tracks, in MIDI channel order
        position = len(self._bus_tracks)  # Start after all bus tracks
        
        # Add offset for channels before this one
        for ch in range(1, midi_channel):
            if ch in self._instrument_tracks:
                position += 1
        
        # Calculate MIDI input value: "All MIDI inputs" on specific channel
        # I_RECINPUT = 4096 | channel | (63 << 5) for "All MIDI inputs" on specific channel
        # 4096 = MIDI input flag, channel = 1-16 for specific channel, (63 << 5) = all MIDI devices
        midi_input_value = 4096 | midi_channel | (63 << 5)
        
        # Create track with all configuration in one call
        track = self.add_track(
            position=position, 
            name=track_name,
            input_value=midi_input_value,
            record_armed=True,
            record_mode=2  # None (monitors input)
        )
        
        # Add to instrument tracks dictionary
        self._instrument_tracks[midi_channel] = track
        
        # Automatically add sends to all existing bus tracks
        for bus_track in self._bus_tracks.values():
            try:
                send_index = track.add_send(bus_track, volume=0.0, mode="post_fx")
                if send_index >= 0:
                    logger.debug(f"Added send from '{track_name}' to bus track '{bus_track.name}' (send index {send_index})")
            except Exception as e:
                logger.warning(f"Failed to add send from '{track_name}' to bus track '{bus_track.name}': {e}")
        
        logger.info(f"Created instrument track '{track_name}' at position {position} for MIDI channel {midi_channel}")
        return track
    
    # def create_16_midi_tracks(self):
    #     """
    #     Creates 16 MIDI tracks in REAPER, one for each MIDI channel.
        
    #     Returns:
    #         List[ReaTrack]: List of created tracks
    #     """
    #     logger.info("Creating 16 MIDI tracks for renardo integration")
    #     tracks = []
        
    #     # Create 16 tracks, one for each MIDI channel
    #     for i in range(1, 17):  # 1 to 16
    #         track = self.create_standard_midi_track(i)
    #         tracks.append(track)
            
    #     logger.info("Successfully created 16 MIDI tracks")
    #     return tracks
    
    def create_bus_track(self, bus_name: str):
        """
        Create a bus track for receiving audio from other tracks.
        Bus tracks are created before instrument tracks to ensure proper routing.

        The track is:
        - Named with the provided bus_name
        - Has no MIDI input (audio only)
        - Not record armed by default
        - Placed before all instrument tracks
        
        Args:
            bus_name: Name for the bus track
            
        Returns:
            ReaTrack: The created bus track
        """
        # Calculate position: at the end of existing bus tracks
        position = len(self._bus_tracks)
        
        # Create track with configuration in one call
        track = self.add_track(
            position=position,
            name=bus_name,
            input_value=-1,  # No MIDI input
            record_armed=False
        )
        
        # Add to bus tracks dictionary with the next available index
        bus_index = len(self._bus_tracks)
        self._bus_tracks[bus_index] = track
        
        # Automatically add sends from all existing instrument tracks to this new bus track
        for instrument_track in self._instrument_tracks.values():
            try:
                send_index = instrument_track.add_send(track, volume=0.0, mode="post_fx")
                if send_index >= 0:
                    logger.debug(f"Added send from '{instrument_track.name}' to bus track '{bus_name}' (send index {send_index})")
            except Exception as e:
                logger.warning(f"Failed to add send from '{instrument_track.name}' to bus track '{bus_name}': {e}")
        
        logger.info(f"Created bus track '{bus_name}' at position {position} (bus index {bus_index})")
        return track
    
    def clear_reaper(self):
        """
        Clear all renardo-related content from REAPER:
        - Remove all ReaperInstruments (which will delete their tracks)
        - Remove all remaining bus tracks
        - Clear internal track lists
        """
        logger.info("Clearing all renardo content from REAPER")
        
        # First, clean up all ReaperInstruments (this clears the Python objects)
        from renardo.reaper_backend.reaper_instrument import ReaperInstrument
        from renardo.reaper_backend.reaper_effect import ReaperEffect
        
        # Clean up ReaperInstruments
        if hasattr(ReaperInstrument, '_instru_facades'):
            instruments_to_remove = ReaperInstrument._instru_facades.copy()
            for instrument in instruments_to_remove:
                try:
                    logger.debug(f"Cleaning up ReaperInstrument: {getattr(instrument, 'shortname', 'unknown')}")
                    # Just clear the Python references, we'll handle REAPER tracks below
                    if instrument in ReaperInstrument._instru_facades:
                        ReaperInstrument._instru_facades.remove(instrument)
                    if hasattr(instrument, '_midi_channel') and instrument._midi_channel in ReaperInstrument._used_track_indexes:
                        ReaperInstrument._used_track_indexes.remove(instrument._midi_channel)
                except Exception as e:
                    logger.warning(f"Error cleaning up instrument {getattr(instrument, 'shortname', 'unknown')}: {e}")
            
            # Clear the class lists
            ReaperInstrument._instru_facades.clear()
            ReaperInstrument._used_track_indexes.clear()
        
        # Clean up ReaperEffects
        if hasattr(ReaperEffect, '_effect_facades'):
            effects_to_remove = ReaperEffect._effect_facades.copy()
            for effect in effects_to_remove:
                try:
                    logger.debug(f"Cleaning up ReaperEffect: {getattr(effect, 'shortname', 'unknown')}")
                    # Just clear the Python references, we'll handle REAPER tracks below
                    if effect in ReaperEffect._effect_facades:
                        ReaperEffect._effect_facades.remove(effect)
                    if hasattr(effect, '_bus_index') and effect._bus_index in ReaperEffect._used_bus_indexes:
                        ReaperEffect._used_bus_indexes.remove(effect._bus_index)
                    if hasattr(effect, 'shortname') and effect.shortname in ReaperEffect.effect_dict:
                        del ReaperEffect.effect_dict[effect.shortname]
                except Exception as e:
                    logger.warning(f"Error cleaning up effect {getattr(effect, 'shortname', 'unknown')}: {e}")
            
            # Clear the class lists
            ReaperEffect._effect_facades.clear()
            ReaperEffect.effect_dict.clear()
            # _used_bus_indexes removed - no bus index tracking needed
        
        # Use REAPER actions to remove all tracks at once (more reliable)
        try:
            # Get current track count
            track_count = self._client.call_reascript_function("CountTracks", self._index)
            logger.debug(f"Found {track_count} tracks to potentially remove")
            
            if track_count > 0:
                # Select all tracks
                self._client.call_reascript_function("Main_OnCommand", 40296, 0)  # Track: Select all tracks
                
                # Remove all selected tracks
                self._client.call_reascript_function("Main_OnCommand", 40005, 0)  # Track: Remove tracks
                
                logger.debug(f"Removed all tracks using REAPER actions")
        
        except Exception as e:
            logger.warning(f"Error using REAPER actions to remove tracks: {e}")
            
            # Fallback: try to remove tracks individually by index (from end to start)
            try:
                track_count = self._client.call_reascript_function("CountTracks", self._index)
                for i in range(track_count - 1, -1, -1):  # Remove from end to start
                    try:
                        track_obj = self._client.call_reascript_function("GetTrack", 0, i)
                        if track_obj:
                            self._client.call_reascript_function("DeleteTrack", track_obj)
                    except Exception as track_err:
                        logger.warning(f"Error removing track at index {i}: {track_err}")
            except Exception as fallback_err:
                logger.warning(f"Fallback track removal also failed: {fallback_err}")
        
        # Clear all internal dictionaries and caches
        self._bus_tracks.clear()
        self._instrument_tracks.clear()
        self.reatracks.clear()
        
        logger.info("Successfully cleared all renardo content from REAPER")