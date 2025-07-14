"""Project-related functionality module."""

import logging
from typing import Optional, List, Union, Dict, Any

logger = logging.getLogger(__name__)

class Project:
    """REAPER project."""
    
    def __init__(self, reaper, index):
        """Initialize the Project object.
        
        Parameters
        ----------
        reaper : Reaper
            Reaper instance.
        index : int
            Project index.
        """
        self._reaper = reaper
        self._client = reaper._client
        self._index = index
        self._tracks = {}  # Cache for Track objects
        
    @property
    def index(self) -> int:
        """Get project index.
        
        Returns
        -------
        int
            Project index.
        """
        return self._index
    
    @property
    def name(self) -> str:
        """Get project name.
        
        Returns
        -------
        str
            Project name.
        """
        # GetProjectName takes project, buf, buf_size
        name = self._client.call_reascript_function("GetProjectName", self._index, "", 1024)
        return name or "Untitled"
    
    @name.setter
    def name(self, value: str) -> None:
        """Set project name.
        
        Parameters
        ----------
        value : str
            New project name.
        """
        self._client.call_reascript_function("GetSetProjectInfo_String", self._index, "PROJECT_NAME", value, True)
    
    @property
    def path(self) -> str:
        """Get project file path.
        
        Returns
        -------
        str
            Project file path or empty string if unsaved.
        """
        # GetProjectPath takes project, buf, buf_size
        path = self._client.call_reascript_function("GetProjectPath", self._index, "", 1024)
        return path
    
    @property
    def length(self) -> float:
        """Get project length in seconds.
        
        Returns
        -------
        float
            Project length in seconds.
        """
        return self._client.call_reascript_function("GetProjectLength", self._index)
    
    @property
    def bpm(self) -> float:
        """Get project tempo.
        
        Returns
        -------
        float
            Project tempo in BPM.
        """
        return self._client.call_reascript_function("GetProjectTimeSignature2", self._index, 0, 0)[0]
    
    @bpm.setter
    def bpm(self, value: float) -> None:
        """Set project tempo.
        
        Parameters
        ----------
        value : float
            New tempo in BPM.
        """
        self._client.call_reascript_function("SetTempoTimeSigMarker", self._index, -1, 0, -1, -1, value, -1, -1, False)
    
    @property
    def time_signature(self) -> tuple:
        """Get project time signature.
        
        Returns
        -------
        tuple
            Tuple of (numerator, denominator).
        """
        _, num, denom = self._client.call_reascript_function("GetProjectTimeSignature2", self._index, 0, 0)
        return (num, denom)
    
    @time_signature.setter
    def time_signature(self, value: tuple) -> None:
        """Set project time signature.
        
        Parameters
        ----------
        value : tuple
            Tuple of (numerator, denominator).
        """
        num, denom = value
        self._client.call_reascript_function("SetTempoTimeSigMarker", self._index, -1, 0, -1, -1, -1, num, denom, False)
    
    @property
    def selected_tracks(self) -> List:
        """Get list of selected tracks.
        
        Returns
        -------
        list of Track
            List of selected tracks.
        """
        from .track import Track
        
        tracks = []
        count = self._client.call_reascript_function("CountSelectedTracks", self._index)
        
        for i in range(count):
            track_id = self._client.call_reascript_function("GetSelectedTrack", self._index, i)
            track_index = self._client.call_reascript_function("GetMediaTrackInfo_Value", track_id, "IP_TRACKNUMBER")
            
            # Track indexes in REAPER are 1-based, but we convert to 0-based
            track_index = int(track_index) - 1
            
            if track_index not in self._tracks:
                self._tracks[track_index] = Track(self, track_index)
                
            tracks.append(self._tracks[track_index])
            
        return tracks
    
    @property
    def tracks(self) -> List:
        """Get list of all tracks.
        
        Returns
        -------
        list of Track
            List of all tracks in the project.
        """
        from .track import Track
        
        tracks = []
        count = self._client.get_track_count()
        
        for i in range(count):
            if i not in self._tracks:
                self._tracks[i] = Track(self, i)
                
            tracks.append(self._tracks[i])
            
        return tracks
    
    def get_track(self, index: int):
        """Get track by index.
        
        Parameters
        ----------
        index : int
            Track index (0-based).
            
        Returns
        -------
        Track
            Track object.
            
        Raises
        ------
        ValueError
            If track with specified index doesn't exist.
        """
        from .track import Track
        
        # Check if track exists
        count = self._client.call_reascript_function("CountTracks", self._index)
        if index < 0 or index >= count:
            raise ValueError(f"Track with index {index} doesn't exist.")
        
        # Check cache and create Track object if needed
        if index not in self._tracks:
            self._tracks[index] = Track(self, index)
            
        return self._tracks[index]
    
    def get_track_by_name(self, name: str, case_sensitive: bool = False):
        """Get track by name.
        
        Parameters
        ----------
        name : str
            Track name to search for.
        case_sensitive : bool, optional
            Whether to perform case-sensitive search. Default=False.
            
        Returns
        -------
        Track or None
            Track object if found, None otherwise.
        """
        from .track import Track
        
        # Get all tracks
        count = self._client.call_reascript_function("CountTracks", self._index)
        
        # Search for track by name
        for i in range(count):
            track_id = self._client.call_reascript_function("GetTrack", self._index, i)
            track_name = self._client.call_reascript_function("GetTrackName", track_id, "", 1024)[2]
            
            if case_sensitive:
                match = track_name == name
            else:
                match = track_name.lower() == name.lower()
                
            if match:
                if i not in self._tracks:
                    self._tracks[i] = Track(self, i)
                    
                return self._tracks[i]
                
        return None
    
    def add_track(self):
        """Add a new track to the project.
        
        Returns
        -------
        Track
            New track object.
        """
        from .track import Track
        
        # Add new track (Action ID: 40001)
        self._reaper.perform_action(40001)
        
        # Get the new track (it will be the last one)
        count = self._client.call_reascript_function("CountTracks", self._index)
        track_index = count - 1
        
        # Create and return Track object
        self._tracks[track_index] = Track(self, track_index)
        return self._tracks[track_index]
    
    def save(self, file_path: Optional[str] = None) -> bool:
        """Save the project.
        
        Parameters
        ----------
        file_path : str, optional
            File path to save the project to. If not provided, uses current path.
            
        Returns
        -------
        bool
            True if save was successful.
        """
        if file_path:
            return self._client.call_reascript_function("Main_SaveProjectEx", self._index, file_path, False)
        else:
            return self._client.call_reascript_function("Main_SaveProject", self._index, False)
    
    def close(self, save: bool = True) -> bool:
        """Close the project.
        
        Parameters
        ----------
        save : bool, optional
            Whether to save before closing. Default=True.
            
        Returns
        -------
        bool
            True if close was successful.
        """
        if save:
            self.save()
        
        return self._client.call_reascript_function("Main_OnCommand", 40860, 0)  # Close current project tab