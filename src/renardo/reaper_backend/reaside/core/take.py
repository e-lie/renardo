"""Take-related functionality module."""

import logging
from typing import Optional, List, Union, Dict, Any

logger = logging.getLogger(__name__)

class Take:
    """REAPER media item take."""
    
    def __init__(self, item, index):
        """Initialize the Take object.
        
        Parameters
        ----------
        item : Item
            Item containing this take.
        index : int
            Take index (0-based).
        """
        self._item = item
        self._track = item._track
        self._project = item._project
        self._reaper = item._reaper
        self._client = item._client
        self._index = index
        self._id = None  # Will be lazily loaded
        
    @property
    def index(self) -> int:
        """Get take index.
        
        Returns
        -------
        int
            Take index (0-based).
        """
        return self._index
    
    @property
    def id(self):
        """Get take ID (MediaTake pointer).
        
        This is used internally for API calls.
        
        Returns
        -------
        int
            Take ID.
        """
        if self._id is None:
            self._id = self._client.call_reascript_function("GetTake", self._item.id, self._index)
        return self._id
    
    @property
    def name(self) -> str:
        """Get take name.
        
        Returns
        -------
        str
            Take name.
        """
        name = self._client.call_reascript_function("GetTakeName", self.id)
        return name or "Unnamed Take"
    
    @name.setter
    def name(self, value: str) -> None:
        """Set take name.
        
        Parameters
        ----------
        value : str
            New take name.
        """
        self._client.call_reascript_function("GetSetMediaItemTakeInfo_String", self.id, "P_NAME", value, True)
    
    @property
    def is_active(self) -> bool:
        """Check if this take is the active take.
        
        Returns
        -------
        bool
            True if this take is active.
        """
        return self._index == self._item.active_take_index
    
    @is_active.setter
    def is_active(self, value: bool) -> None:
        """Set this take as the active take.
        
        Parameters
        ----------
        value : bool
            True to set as active, False has no effect.
        """
        if value:
            self._client.call_reascript_function("SetActiveTake", self.id)
    
    @property
    def start_offset(self) -> float:
        """Get take start offset.
        
        Returns
        -------
        float
            Start offset in seconds.
        """
        return self._client.call_reascript_function("GetMediaItemTakeInfo_Value", self.id, "D_STARTOFFS")
    
    @start_offset.setter
    def start_offset(self, value: float) -> None:
        """Set take start offset.
        
        Parameters
        ----------
        value : float
            New start offset in seconds.
        """
        self._client.call_reascript_function("SetMediaItemTakeInfo_Value", self.id, "D_STARTOFFS", value)
    
    @property
    def source_length(self) -> float:
        """Get take source media length.
        
        Returns
        -------
        float
            Source length in seconds.
        """
        source = self._client.call_reascript_function("GetMediaItemTake_Source", self.id)
        if not source:
            return 0.0
        
        return self._client.call_reascript_function("GetMediaSourceLength", source)
    
    @property
    def playback_rate(self) -> float:
        """Get take playback rate.
        
        Returns
        -------
        float
            Playback rate (1.0 is normal speed).
        """
        return self._client.call_reascript_function("GetMediaItemTakeInfo_Value", self.id, "D_PLAYRATE")
    
    @playback_rate.setter
    def playback_rate(self, value: float) -> None:
        """Set take playback rate.
        
        Parameters
        ----------
        value : float
            New playback rate (1.0 is normal speed).
        """
        self._client.call_reascript_function("SetMediaItemTakeInfo_Value", self.id, "D_PLAYRATE", value)
    
    @property
    def pitch(self) -> float:
        """Get take pitch adjustment.
        
        Returns
        -------
        float
            Pitch adjustment in semitones.
        """
        return self._client.call_reascript_function("GetMediaItemTakeInfo_Value", self.id, "D_PITCH")
    
    @pitch.setter
    def pitch(self, value: float) -> None:
        """Set take pitch adjustment.
        
        Parameters
        ----------
        value : float
            New pitch adjustment in semitones.
        """
        self._client.call_reascript_function("SetMediaItemTakeInfo_Value", self.id, "D_PITCH", value)
    
    @property
    def is_midi(self) -> bool:
        """Check if this take contains MIDI data.
        
        Returns
        -------
        bool
            True if this take contains MIDI data.
        """
        source = self._client.call_reascript_function("GetMediaItemTake_Source", self.id)
        if not source:
            return False
        
        return self._client.call_reascript_function("GetMediaSourceType", source) == "MIDI"
    
    def get_midi_notes(self) -> List[Dict]:
        """Get MIDI notes in this take.
        
        Returns
        -------
        list of dict
            List of dictionaries with note information.
            
        Raises
        ------
        RuntimeError
            If take doesn't contain MIDI data.
        """
        if not self.is_midi:
            raise RuntimeError("Take doesn't contain MIDI data.")
        
        # Get MIDI editor for this take
        editor = self._client.call_reascript_function("MIDIEditor_GetActive")
        if not editor:
            # Create a temporary editor and get notes
            self._client.call_reascript_function("Main_OnCommand", 40153, 0)  # Open MIDI editor
            editor = self._client.call_reascript_function("MIDIEditor_GetActive")
            
            if not editor:
                raise RuntimeError("Failed to open MIDI editor.")
        
        # Get notes
        notes = []
        count = self._client.call_reascript_function("MIDI_CountEvts", self.id)
        
        for i in range(count):
            # MIDI_GetNote returns (retval, take, noteidx, selectedOut, mutedOut, startppqposOut, endppqposOut, chanOut, pitchOut, velOut)
            _, _, _, selected, muted, start_ppq, end_ppq, channel, pitch, velocity = (
                self._client.call_reascript_function("MIDI_GetNote", self.id, i)
            )
            
            notes.append({
                "index": i,
                "selected": selected,
                "muted": muted,
                "start_ppq": start_ppq,
                "end_ppq": end_ppq,
                "length_ppq": end_ppq - start_ppq,
                "channel": channel,
                "pitch": pitch,
                "velocity": velocity
            })
        
        return notes
    
    def add_midi_note(self, pitch: int, start_ppq: float, length_ppq: float, channel: int = 0, velocity: int = 100) -> bool:
        """Add a MIDI note to this take.
        
        Parameters
        ----------
        pitch : int
            MIDI note pitch (0-127).
        start_ppq : float
            Start position in PPQ.
        length_ppq : float
            Note length in PPQ.
        channel : int, optional
            MIDI channel (0-15). Default=0.
        velocity : int, optional
            Note velocity (0-127). Default=100.
            
        Returns
        -------
        bool
            True if note was added successfully.
            
        Raises
        ------
        RuntimeError
            If take doesn't contain MIDI data.
        """
        if not self.is_midi:
            raise RuntimeError("Take doesn't contain MIDI data.")
        
        # Add note
        return self._client.call_reascript_function(
            "MIDI_InsertNote",
            self.id,
            False,  # selected
            False,  # muted
            start_ppq,
            start_ppq + length_ppq,
            channel,
            pitch,
            velocity,
            True  # noSort
        )
    
    def delete(self) -> bool:
        """Delete this take.
        
        Returns
        -------
        bool
            True if deletion was successful.
            
        Raises
        ------
        RuntimeError
            If this is the only take in the item.
        """
        if len(self._item.takes) <= 1:
            raise RuntimeError("Cannot delete the only take in an item.")
        
        # Make this the active take
        self.is_active = True
        
        # Delete active take
        return self._reaper.perform_action(40129)  # Delete active take