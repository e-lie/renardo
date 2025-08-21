"""
REAPER music resource implementations for Renardo.

This module provides REAPER-specific implementations of the 
generic music resource classes from renardo.lib.music_resource.
"""

from typing import Dict, Any, Optional, Mapping, List, Tuple, ClassVar, TYPE_CHECKING
from pathlib import Path
import shutil
import inspect

from renardo.lib.InstrumentProxy import InstrumentProxy
from renardo.lib.music_resource import Instrument
from renardo.lib.Extensions.MidiMapFactory import MidiMapFactory
from renardo.sc_backend.Midi import ReaperInstrumentProxy
from renardo.lib.Patterns import Pattern
from renardo.logger import get_logger

# Import the base ReaperResource class
from renardo.reaper_backend.reaper_resource import ReaperResource

logger = get_logger('reaper_backend.reaper_instrument')



class ReaperInstrument(Instrument, ReaperResource):
    """Represents a REAPER instrument using reaside."""
    # Class-level attributes specific to instruments
    _used_track_indexes: ClassVar[List[int]] = []
    _instru_facades: ClassVar[List['ReaperInstrument']] = []

    def __init__(
            self,
            shortname: str,
            fxchain_path: str,
            arguments: Dict[str, Any] = None,
            fullname: Optional[str] = None,
            description: Optional[str] = None,
            bank: str = "undefined",
            category: str = "undefined",
    ):
        """
        Initialize a REAPER instrument linked to REAPER.
        Creates a track with the instrument's shortname and loads the FXChain.
        
        Args:
            shortname: Short name used as identifier
            fxchain_path: Path to the REAPER FX chain file
            arguments: Dictionary of argument names and default values
            fullname: Full descriptive name
            description: Longer description of the instrument
            bank: The resource bank this belongs to
            category: The category within the bank
        """
        # Initialize both parent classes
        Instrument.__init__(self, shortname, fullname, description, arguments, bank, category)
        ReaperResource.__init__(self, shortname, fxchain_path, arguments, fullname, description, bank, category)

        self.instrument_loaded = False
        self.plugin_name = shortname
        
        # Initialize instrument-specific functionality
        self._initialize_instrument()
        
        # Add to class instances list for tracking
        self.__class__._instru_facades.append(self)
    
    def _initialize_instrument(self):
        """Initialize the instrument by creating a track and loading FX chain."""
        try:
            # Find an available midi channel
            first_available_midi_channel = self.__class__.find_available_midi_channel()
            if first_available_midi_channel is not None:
                self._midi_channel = first_available_midi_channel
            else:
                raise Exception(f"No available MIDI channel found for {self.shortname}")
            
            # Reserve this channel immediately to prevent conflicts
            if self._midi_channel not in self.__class__._used_track_indexes:
                self.__class__._used_track_indexes.append(self._midi_channel)
            
            # Ensure FXChain is in REAPER
            self.ensure_fxchain_in_reaper()
            
            # Get or create track using reaside
            self._reatrack = self.__class__._project.get_track_by_name(self.track_name)
            
            if not self._reatrack:
                # Create the track if it doesn't exist
                self._reatrack = self.__class__._project.create_instrument_track(
                    track_name=self.track_name,
                    midi_channel=self._midi_channel
                )
            
            # Use reaside to load the FX chain
            try:
                fx_added = self._reatrack.add_fxchain(self.plugin_name)
                if fx_added > 0:
                    # Rescan track to get FX objects
                    self._reatrack.rescan_fx()
                    # Get the first FX as the instrument
                    fx_list = self._reatrack.list_fx()
                    if fx_list:
                        self._reafx_instrument = fx_list[0]
                        self._fx_list = fx_list  # Store for base class
                    else:
                        self._reafx_instrument = None
                else:
                    self._reafx_instrument = None
            except Exception as e:
                logger.error(f"Failed to load FX chain {self.plugin_name}: {e}")
                self._reafx_instrument = None
                
            logger.info(f"ReaperInstrument '{self.shortname}' initialized on track '{self.track_name}' (MIDI ch {self._midi_channel})")
            
        except Exception as e:
            logger.error(f"Failed to initialize ReaperInstrument '{self.shortname}': {e}")
            raise


    @classmethod
    def find_available_midi_channel(cls):
        free_midi_channels = [index for index in range(1, 17) if index not in cls._used_track_indexes]
        if not free_midi_channels:
            logger.error("No free track indexes available.")
            return None
        return free_midi_channels[0]

    @classmethod
    def is_channel_available(cls, channel_num):
        return channel_num not in cls._used_track_indexes
        
    @classmethod
    def set_class_attributes(cls, presets: Mapping, reaper_instance=None, project=None, resource_library=None):
        """Initialize the class-level attributes for reaside."""
        # Call parent method
        super().set_class_attributes(presets, reaper_instance, project, resource_library)
        
        # Initialize instrument-specific attributes
        cls._used_track_indexes = []
        cls._instru_facades = []
    
    @classmethod
    def update_used_track_indexes(cls):
        """Update the list of track indexes that are currently in use."""
        if not cls._project:
            return
        for i in range(16):
            track_name = "chan" + str(i+1)
            track = cls._project.get_track_by_name(track_name)
            if track:
                fx_count = track.get_fx_count()
                if fx_count > 0 and i+1 not in cls._used_track_indexes:
                    cls._used_track_indexes.append(i+1)
                elif i+1 in cls._used_track_indexes and fx_count == 0:
                    cls._used_track_indexes = [index for index in cls._used_track_indexes if index != i+1]
    
    # add_effect_plugin method inherited from ReaperResource
    
    # apply_all_existing_reaper_params method inherited from ReaperResource

    def __call__(self, *args, sus=None, **kwargs):
        """
        Create an instrument proxy for use with a Player.
        
        Args:
            *args: Positional arguments (typically note degree or MIDI note)
            sus: Sustain pattern
            **kwargs: Additional keyword arguments
            
        Returns:
            InstrumentProxy or ReaperInstrumentProxy: A proxy configured with this instrument
        """
        # If using original behavior (no REAPER project)
        if not hasattr(self, '_project') or not self._project:
            # Use original InstrumentProxy behavior
            degree = args[0] if args else None
            return InstrumentProxy(self.shortname, degree, kwargs)
        
        # Use extended REAPER behavior (merged from former ReaperInstrumentFacade)
        config_defaults = {}
        
        if "track_default" in self._presets.keys():
            config_defaults = self._presets["track_default"]

        preset_name = self._reatrack.name + "_default"
        if preset_name in self._presets.keys():
            config_defaults = config_defaults | self._presets[preset_name]

        # Get FX objects from reaside track
        fx_objects = self._reatrack.list_fx()
        for fx_obj in fx_objects:
            fx_name = fx_obj.snake_name  # Use snake_name for consistency
            preset_name = fx_name + "_default"
            #by default all fxs are off
            if 'fx_reset' in kwargs and kwargs['fx_reset']:
                config_defaults[fx_name+'_on'] = False
            if preset_name in self._presets.keys():
                config_defaults = config_defaults | self._presets[preset_name]

        params = config_defaults | kwargs  # overwrite gathered default config with runtime arguments

        remaining_param_dict = {}
        self.apply_all_existing_reaper_params(self._reatrack, params, remaining_param_dict, runtime_kwargs=kwargs)

        # No midi_map handling needed anymore

        # to avoid midi event collision between start and end note (which prevent the instrument from playing)
        dur = remaining_param_dict["dur"] if "dur" in remaining_param_dict.keys() else 1
        sus = Pattern(sus) if sus is not None else Pattern(dur)-0.03

        return ReaperInstrumentProxy(
            reatrack=self._reatrack,
            channel=self._midi_channel - 1,
            sus=sus,
            *args,
            **remaining_param_dict,
        )
    
    def delete(self):
        """Manually clean up the instrument and remove its track."""
        try:
            # Remove from class instances list
            if self in self.__class__._instru_facades:
                self.__class__._instru_facades.remove(self)
            
            # Delete the track in REAPER if it exists
            track_index_to_clean = None
            if hasattr(self, '_reatrack') and self._reatrack:
                try:
                    track_index_to_clean = self._reatrack.index
                    
                    # Clear all FX from the track first
                    fx_count = self._reatrack.get_fx_count()
                    for i in range(fx_count - 1, -1, -1):  # Remove from end to start
                        track_obj = self._reatrack._client.call_reascript_function("GetTrack", 0, self._reatrack.index)
                        if track_obj:
                            self._reatrack._client.call_reascript_function("TrackFX_Delete", track_obj, i)
                    
                    # Delete the track itself
                    self._reatrack.delete()
                    logger.info(f"Deleted track {self.track_name} for instrument {self.shortname}")
                except Exception as e:
                    logger.warning(f"Could not delete track for instrument {self.shortname}: {e}")
            
            # Clean up project track cache - remove stale references
            if self.__class__._project and track_index_to_clean is not None:
                try:
                    # Remove from main track cache
                    if track_index_to_clean in self.__class__._project.reatracks:
                        del self.__class__._project.reatracks[track_index_to_clean]
                    
                    # Remove from instrument tracks cache if it was an instrument track
                    if hasattr(self, '_midi_channel'):
                        if self._midi_channel in self.__class__._project._instrument_tracks:
                            del self.__class__._project._instrument_tracks[self._midi_channel]
                    
                    # Also clean up any tracks that were shifted due to deletion
                    # When a track is deleted, all tracks after it shift down by one index
                    tracks_to_update = {}
                    for idx in list(self.__class__._project.reatracks.keys()):
                        if idx > track_index_to_clean:
                            # This track was shifted down
                            track = self.__class__._project.reatracks[idx]
                            track._index = idx - 1  # Update the internal index
                            tracks_to_update[idx - 1] = track
                            del self.__class__._project.reatracks[idx]
                    
                    # Add the updated tracks back
                    self.__class__._project.reatracks.update(tracks_to_update)
                    
                    logger.debug(f"Cleaned up project track cache after deleting track {track_index_to_clean}")
                    
                except Exception as e:
                    logger.warning(f"Could not clean up project track cache: {e}")
            
            # Release the MIDI channel
            if hasattr(self, '_midi_channel') and self._midi_channel in self.__class__._used_track_indexes:
                self.__class__._used_track_indexes.remove(self._midi_channel)
                logger.debug(f"Released MIDI channel {self._midi_channel} for instrument {self.shortname}")
            
            # Clear references
            if hasattr(self, '_reafx_instrument'):
                self._reafx_instrument = None
            if hasattr(self, '_reatrack'):
                self._reatrack = None
                
        except Exception as e:
            logger.error(f"Error cleaning up ReaperInstrument {getattr(self, 'shortname', 'unknown')}: {e}")
        
        # Call parent delete method for additional cleanup  
        super().delete()
    
    def add_send(self, destination_track, volume: float = 0.0, pan: float = 0.0, 
                 mute: bool = False, mode: str = "post_fx"):
        """
        Add a send from this instrument's track to another track (typically a bus).
        
        Args:
            destination_track: The destination ReaTrack, track index, or track name to send to
            volume: Send volume (0.0 to 1.0, default 0.0)
            pan: Send pan (-1.0 to 1.0, default 0.0 center)
            mute: Whether the send should be muted (default False)
            mode: Send mode - "pre_fx" (pre-fader pre-fx), "post_fx" (pre-fader post-fx), "post_fader" (post-fader pre-fx) (default "post_fx")
            
        Returns:
            int: The send index that was created, or -1 if failed
        """
        if not hasattr(self, '_reatrack') or not self._reatrack:
            logger.error(f"No track associated with instrument '{self.shortname}'")
            return -1
            
        return self._reatrack.add_send(destination_track, volume, pan, mute, mode)

    # load method inherited from ReaperResource


    # ensure_fxchain_in_reaper method inherited from ReaperResource

    # list_parameters method inherited from ReaperResource
    

