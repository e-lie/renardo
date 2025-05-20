from typing import Mapping
from pprint import pprint
from pathlib import Path

from renardo.reaper_backend.reaper_music_resource import ReaperInstrument
from renardo.reaper_backend.ReaperIntegrationLib.ReaProject import ReaProject
from renardo.reaper_backend.ReaperIntegrationLib.ReaTrack import ReaTrack
from renardo.reaper_backend.ReaperIntegrationLib.ReaTaskQueue import ReaTask
from renardo.settings_manager import settings, SettingsManager



def init_reapy_project(clock):
    """Initialize a REAPER project.
    
    Returns:
        ReaProject: An initialized ReaProject instance, or None if initialization failed
    """
    project = None
    try:
        import reapy
        project = ReaProject(clock, reapylib=reapy)
    except Exception as err:
        output = err.message if hasattr(err, 'message') else err
        print(f"Error scanning and initializing Reaper project: {output} -> skipping Reaper integration")
    return project


# # For backwards compatibility, create a ReaperInstrumentFactory class that delegates to ReaperInstrument
# class ReaperInstrumentFactory:
#     """
#     Factory for creating REAPER instruments.
    
#     Note: This class is provided for backwards compatibility.
#     New code should use the class methods on ReaperInstrument directly.
#     """

#     def __init__(self, presets: Mapping, project: ReaProject) -> None:
#         """
#         Initialize the factory.
        
#         Args:
#             presets: Dictionary of preset configurations
#             project: ReaProject instance for REAPER integration
#         """
#         # Initialize the ReaperInstrument class with our settings
#         ReaperInstrument.set_class_attributes(presets, project)
        
#         # Store references for compatibility
#         self._presets = presets
#         self._reaproject = project
#         self.used_track_indexes = ReaperInstrument._used_track_indexes
#         self.instru_facades = ReaperInstrument._instru_facades
#         self._resource_library = ReaperInstrument._resource_library

#     def update_used_track_indexes(self):
#         """Update the list of track indexes that are currently in use."""
#         ReaperInstrument.update_used_track_indexes()
#         # Update our reference
#         self.used_track_indexes = ReaperInstrument._used_track_indexes

#     def create_all_facades_from_reaproject_tracks(self):
#         """Create instrument facades for all tracks in the REAPER project."""
#         return ReaperInstrument.create_all_facades_from_reaproject_tracks()

#     def create_instrument_facade(self, name, plugin_name=None, track_name=None, preset=None, params={}, scan_all_params=True, is_chain=True):
#         """Create a REAPER instrument facade."""
#         return ReaperInstrument.create_instrument_facade(name, plugin_name, track_name, preset, params, scan_all_params, is_chain)
    
#     def add_multiple_fxchains(self, *args, scan_all_params=True, is_chain=True):
#         """Add multiple FX chains to REAPER."""
#         return ReaperInstrument.add_multiple_fxchains(*args, scan_all_params=scan_all_params, is_chain=is_chain)
    
#     def ensure_fxchain_in_reaper(self, shortname: str):
#         """
#         Ensure that a FXChain is available in REAPER.
        
#         Args:
#             shortname: The short name of the FXChain resource to install
            
#         Returns:
#             bool: True if the FXChain was successfully installed or already exists, False otherwise
#         """
#         return ReaperInstrument.ensure_fxchain_in_reaper(shortname)


