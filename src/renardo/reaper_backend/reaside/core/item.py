"""Item-related functionality module."""

import logging
from typing import Optional, List, Union, Dict, Any

logger = logging.getLogger(__name__)

class ReaItem:
    """REAPER media item."""
    
    def __init__(self, track, index):
        """Initialize the Item object."""
        self._track = track
        self._project = track._project
        self._reaper = track._reaper
        self._client = track._client
        self._index = index
        self._id = None  # Will be lazily loaded
        self._takes = {}  # Cache for Take objects
        
    @property
    def index(self) -> int:
        """Get item index."""
        return self._index
    
    @property
    def id(self):
        """Get item ID (MediaItem pointer)."""
        if self._id is None:
            self._id = self._client.call_reascript_function("GetTrackMediaItem", self._track.id, self._index)
        return self._id
    
    @property
    def name(self) -> str:
        """Get item name."""
        notes = self._client.call_reascript_function("GetSetMediaItemInfo_String", self.id, "P_NOTES", "", False)
        if notes:
            return notes
        
        # If no notes, use the active take name
        take = self.active_take
        if take:
            return take.name
        
        return "Unnamed Item"
    
    @name.setter
    def name(self, value: str) -> None:
        """Set item name."""
        self._client.call_reascript_function("GetSetMediaItemInfo_String", self.id, "P_NOTES", value, True)
    
    @property
    def position(self) -> float:
        """Get item position."""
        return self._client.call_reascript_function("GetMediaItemInfo_Value", self.id, "D_POSITION")
    
    @position.setter
    def position(self, value: float) -> None:
        """Set item position."""
        self._client.call_reascript_function("SetMediaItemInfo_Value", self.id, "D_POSITION", value)
    
    @property
    def length(self) -> float:
        """Get item length."""
        return self._client.call_reascript_function("GetMediaItemInfo_Value", self.id, "D_LENGTH")
    
    @length.setter
    def length(self, value: float) -> None:
        """Set item length."""
        self._client.call_reascript_function("SetMediaItemInfo_Value", self.id, "D_LENGTH", value)
    
    @property
    def is_selected(self) -> bool:
        """Check if item is selected."""
        return bool(self._client.call_reascript_function("GetMediaItemInfo_Value", self.id, "B_UISEL"))
    
    @is_selected.setter
    def is_selected(self, value: bool) -> None:
        """Set item selection state."""
        self._client.call_reascript_function("SetMediaItemSelected", self.id, value)
    
    @property
    def is_muted(self) -> bool:
        """Check if item is muted."""
        return bool(self._client.call_reascript_function("GetMediaItemInfo_Value", self.id, "B_MUTE"))
    
    @is_muted.setter
    def is_muted(self, value: bool) -> None:
        """Set item mute state."""
        self._client.call_reascript_function("SetMediaItemInfo_Value", self.id, "B_MUTE", value)
    
    @property
    def takes(self) -> List:
        """Get list of all takes in this item."""
        from .take import ReaTake
        
        takes = []
        count = self._client.call_reascript_function("GetMediaItemNumTakes", self.id)
        
        for i in range(count):
            if i not in self._takes:
                self._takes[i] = ReaTake(self, i)
                
            takes.append(self._takes[i])
            
        return takes
    
    @property
    def active_take_index(self) -> int:
        """Get active take index."""
        count = self._client.call_reascript_function("GetMediaItemNumTakes", self.id)
        if count == 0:
            return -1
            
        take_id = self._client.call_reascript_function("GetActiveTake", self.id)
        if not take_id:
            return -1
            
        # Find the take index
        for i in range(count):
            test_id = self._client.call_reascript_function("GetTake", self.id, i)
            if test_id == take_id:
                return i
                
        return -1
    
    @active_take_index.setter
    def active_take_index(self, value: int) -> None:
        """Set active take by index."""
        count = self._client.call_reascript_function("GetMediaItemNumTakes", self.id)
        if value < 0 or value >= count:
            raise ValueError(f"Take index {value} out of range (0-{count-1}).")
            
        take_id = self._client.call_reascript_function("GetTake", self.id, value)
        self._client.call_reascript_function("SetActiveTake", take_id)
    
    @property
    def active_take(self):
        """Get the active take."""
        from .take import ReaTake
        
        index = self.active_take_index
        if index < 0:
            return None
            
        if index not in self._takes:
            self._takes[index] = ReaTake(self, index)
            
        return self._takes[index]
    
    def get_take(self, index: int):
        """Get take by index."""
        from .take import ReaTake
        
        # Check if take exists
        count = self._client.call_reascript_function("GetMediaItemNumTakes", self.id)
        if index < 0 or index >= count:
            raise ValueError(f"Take with index {index} doesn't exist.")
        
        # Check cache and create Take object if needed
        if index not in self._takes:
            self._takes[index] = ReaTake(self, index)
            
        return self._takes[index]
    
    def add_take(self):
        """Add a new empty take to the item."""
        from .take import ReaTake
        
        # Add new take (select item first)
        self.is_selected = True
        self._reaper.perform_action(40124)  # Item: Add new take
        
        # Get the new take (it will be the last one)
        count = self._client.call_reascript_function("GetMediaItemNumTakes", self.id)
        take_index = count - 1
        
        # Create and return Take object
        self._takes[take_index] = ReaTake(self, take_index)
        return self._takes[take_index]
    
    def delete(self) -> bool:
        """Delete this item."""
        # Select only this item
        self._client.call_reascript_function("SetMediaItemSelected", self.id, True)
        
        # Delete selected items
        return self._reaper.perform_action(40006)  # Remove items