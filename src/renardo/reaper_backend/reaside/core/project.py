"""Project-related functionality module."""

from renardo.logger import get_logger
from typing import Optional, List, Union, Dict, Any

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
        """Get project name."""
        # Try to get from project title first
        result = self._client.call_reascript_function("GetSetProjectInfo_String", 0, "PROJECT_TITLE", "", False)
        if isinstance(result, tuple) and len(result) >= 2 and result[1]:
            return result[1]
            
        # Fallback to ExtState if available
        title = self._client.get_ext_state("project", "title")
        if title:
            return title
            
        # Final fallback to GetProjectName
        name = self._client.call_reascript_function("GetProjectName", self._index, "", 1024)
        return name or "Untitled"
    
    @name.setter
    def name(self, value: str) -> None:
        """Set project name."""
        # Use PROJECT_TITLE to set the project title
        self._client.call_reascript_function("GetSetProjectInfo_String", 0, "PROJECT_TITLE", value, True)
        
        # Also store in ExtState as backup
        self._client.set_ext_state("project", "title", value)
    
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
    
    def add_track(self, position: Optional[int] = None):
        """Add a new track to the project at the specified position.
        
        Args:
            position: Track index where to insert (0-based). If None, adds at the end.
            
        Returns:
            ReaTrack: The newly created track
        """
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
            # We need to update tracks that were at or after the insertion point
            for idx in sorted(self.reatracks.keys(), reverse=True):
                if idx >= position:
                    # This track was shifted down by one
                    track = self.reatracks[idx]
                    track._index = idx + 1
                    # Move it in the cache
                    del self.reatracks[idx]
                    self.reatracks[idx + 1] = track
        
        # Create and return Track object (this will automatically scan it)
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
        - Set to receive from "All MIDI inputs"
        - Set to receive from the specified MIDI channel
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
        
        # Add track at the calculated position
        track = self.add_track(position)
        track.name = track_name
        
        # Get track object
        track_obj = self._client.call_reascript_function("GetTrack", 0, track._index)
        
        # Set MIDI input to "All MIDI inputs" on the appropriate channel
        # ReaScript: I_RECINPUT = 4096 | channel | (63 << 5) for "All MIDI inputs" on specific channel
        # 4096 = MIDI input flag, channel = 1-16 for specific channel, (63 << 5) = all MIDI devices
        midi_input_value = 4096 | midi_channel | (63 << 5)
        self._client.call_reascript_function("SetMediaTrackInfo_Value", track_obj, "I_RECINPUT", midi_input_value)
        
        # Arm the track for recording
        track.is_armed = True
        
        # Set record mode to "2 = None (monitors input)"
        self._client.call_reascript_function("SetMediaTrackInfo_Value", track_obj, "I_RECMODE", 2)
        
        # Add to instrument tracks dictionary
        self._instrument_tracks[midi_channel] = track
        
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
        
        # Add track at the calculated position
        track = self.add_track(position)
        track.name = bus_name
        
        # Get track object
        track_obj = self._client.call_reascript_function("GetTrack", 0, track._index)
        
        # Bus tracks don't need MIDI input, so we set I_RECINPUT to -1 (no input)
        self._client.call_reascript_function("SetMediaTrackInfo_Value", track_obj, "I_RECINPUT", -1)
        
        # Bus tracks are typically not record armed
        track.is_armed = False
        
        # Add to bus tracks dictionary with the next available index
        bus_index = len(self._bus_tracks)
        self._bus_tracks[bus_index] = track
        
        logger.info(f"Created bus track '{bus_name}' at position {position} (bus index {bus_index})")
        return track