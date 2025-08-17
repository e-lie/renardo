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
    
    def add_track(self):
        """Add a new track to the project."""
        # Add new track (Action ID: 40001)
        self._reaper.perform_action(40001)
        
        # Get the new track (it will be the last one)
        count = self._client.call_reascript_function("CountTracks", self._index)
        track_index = count - 1
        
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
    
    def create_standard_midi_track(self, track_num: int):
        """
        Create a MIDI track for renardo integration.

        The track is:
        - Named chan1 to 16 from track_num
        - Record armed
        - Set to receive from "All MIDI inputs"
        - Set to receive from the MIDI channel corresponding to its number
        - Record mode set to "Stereo Out" (monitors the track output)
        
        Args:
            track_num: MIDI channel number (1-16)
            
        Returns:
            ReaTrack: The created track
        """
        # Create track with name "chanX" where X is the channel number
        track_name = f"chan{track_num}"
        
        # Add track and get its index
        track = self.add_track()
        track.name = track_name
        
        # Set MIDI input to "All MIDI inputs" on the appropriate channel
        # ReaScript: I_RECINPUT = 4096 | channel | (63 << 5) for "All MIDI inputs" on specific channel
        # 4096 = MIDI input flag, channel = 1-16 for specific channel, (63 << 5) = all MIDI devices
        midi_input_value = 4096 | track_num | (63 << 5)
        track_obj = self._client.call_reascript_function("GetTrack", 0, track._index)
        self._client.call_reascript_function("SetMediaTrackInfo_Value", track_obj, "I_RECINPUT", midi_input_value)
        
        # Arm the track for recording
        track.is_armed = True
        
        # Set record mode to "2 = None (monitors input)"
        self._client.call_reascript_function("SetMediaTrackInfo_Value", track_obj, "I_RECMODE", 2)
        
        logger.info(f"Created MIDI track '{track_name}' for channel {track_num}")
        return track
    
    def create_16_midi_tracks(self):
        """
        Creates 16 MIDI tracks in REAPER, one for each MIDI channel.
        
        Returns:
            List[ReaTrack]: List of created tracks
        """
        logger.info("Creating 16 MIDI tracks for renardo integration")
        tracks = []
        
        # Create 16 tracks, one for each MIDI channel
        for i in range(1, 17):  # 1 to 16
            track = self.create_standard_midi_track(i)
            tracks.append(track)
            
        logger.info("Successfully created 16 MIDI tracks")
        return tracks