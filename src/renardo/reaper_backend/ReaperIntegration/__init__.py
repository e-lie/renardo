
from typing import Mapping
from pprint import pprint
from pathlib import Path

from renardo.runtime import Clock, player_method

from renardo.reaper_backend.reaper_music_resource import ReaperInstrument
from renardo.reaper_backend.ReaperIntegrationLib.ReaProject import ReaProject
from renardo.reaper_backend.ReaperIntegrationLib.ReaTrack import ReaTrack
from renardo.reaper_backend.ReaperIntegrationLib.ReaTaskQueue import ReaTask
from renardo.settings_manager import settings, SettingsManager
from renardo.gatherer.reaper_resource_management.reaper_resource_library import ReaperResourceLibrary
from renardo.lib.music_resource import ResourceType

def init_reapy_project():
    project = None
    try:
        import reapy
        project = ReaProject(Clock, reapylib=reapy)
    except Exception as err:
        output = err.message if hasattr(err, 'message') else err
        print("Error scanning and initializing Reaper project: {output} -> skipping Reaper integration".format(output=output))
    return project

class ReaperInstrumentFactory:

    def __init__(self, presets: Mapping, project: ReaProject) -> None:
        self._presets = presets
        self._reaproject = project
        self.used_track_indexes = []
        self.instru_facades = []
        self._resource_library = None

    def update_used_track_indexes(self):
        for i in range(16):
            if len(self._reaproject.reatracks["chan"+str(i+1)].reafxs) != 0 and i+1 not in self.used_track_indexes:
                self.used_track_indexes.append(i+1)
            elif i+1 in self.used_track_indexes and len(self._reaproject.reatracks["chan"+str(i+1)].reafxs) == 0:
                self.used_track_indexes = [index for index in self.used_track_indexes if index != i+1]

    def create_all_facades_from_reaproject_tracks(self):
        instrument_dict = {}
        for reatrack in self._reaproject.bus_tracks:
            instrument_dict[reatrack.name[1:]] = self.create_instrument_facade(track_name=reatrack.name, midi_channel=-1)

        for i, track in enumerate(self._reaproject.instrument_tracks):
            if len(track.reafxs.values()) > 0:
                instrument_name = list(track.reafxs.values())[0].name # first fx is the usually the synth/instrument that give the name
            else:
                instrument_name = track.name # if not exist, use the less interesting track name (chan2...)
            instrument_kwargs = {
                "track_name": track.name,
                "midi_channel": i + 1,
            }
            instrument_dict[instrument_name] = self.create_instrument_facade(**instrument_kwargs)
        return instrument_dict

    def create_instrument_facade(self, name, plugin_name=None, track_name=None, preset=None, params={}, scan_all_params=True, is_chain=True):
        midi_channel = -1
        if plugin_name is None:
            plugin_name = name
        if track_name is None:
            free_indexes = [index for index in range(1,17) if index not in self.used_track_indexes]
            free_index = free_indexes[0]
            midi_channel = free_index
            self.used_track_indexes.append(free_index)
            track_name='chan'+str(free_index)
        elif track_name[:4] == 'chan':
            try:
                midi_channel = int(track_name[4:6])
            except Exception:
                midi_channel = int(track_name[4:5])
        if preset is None:
            preset = name
        try:
            return ReaperInstrument(
                shortname=name,
                fullname=name,
                description=f"ReaperInstrument for {name}",
                fxchain_relative_path="",
                reaproject=self._reaproject,
                presets=self._presets,
                track_name=track_name,
                midi_channel=midi_channel,
                create_instrument=True,
                instrument_name=name,
                plugin_name=plugin_name,
                plugin_preset=preset,
                instrument_params=params,
                scan_all_params=scan_all_params,
                is_chain=is_chain
            )
        except Exception as err:
            output = err.message if hasattr(err, 'message') else err
            print("Error creating instrument {name}: {output} -> skipping".format(name=name, output=output))
            return None
    
    def add_multiple_fxchains(*args, scan_all_params=True, is_chain=True):
        facades = []
        # args[0] is self is the instru factory
        selff = args[0]
        for chain in args[1:]:
            try:
                facade = selff.create_instrument_facade(chain, chain, scan_all_params=scan_all_params, is_chain=is_chain)
            except Exception as e:
                print(f"Error adding chain {chain}: {e}")
            if facade:
                facades.append(facade)
        selff.instru_facades += facades
        return tuple([facade.out for facade in facades])
    
    def ensure_fxchain_in_reaper(self, shortname: str):
        """
        Ensure that a FXChain from the ReaperResourceLibrary is present in REAPER's FXChains directory.
        
        Args:
            shortname: The short name of the FXChain resource to install
            
        Returns:
            bool: True if the FXChain was successfully installed or already exists, False otherwise
        """
        try:
            # Get the Renardo FXChains directory in REAPER's config
            config_dir = SettingsManager.get_standard_config_dir()
            reaper_fxchains_dir = config_dir / "REAPER" / "FXChains"
            renardo_fxchains_dir = reaper_fxchains_dir / "renardo_fxchains"
            
            # Create the renardo_fxchains directory if it doesn't exist
            renardo_fxchains_dir.mkdir(parents=True, exist_ok=True)
            
            # Get the resource library if not already loaded
            if self._resource_library is None:
                # Use the renardo resources path
                resources_path = settings.get_path("RENARDO_ROOT_PATH") / "reaper_resources"
                if resources_path.exists():
                    self._resource_library = ReaperResourceLibrary(resources_path)
                else:
                    print(f"Reaper resources directory not found: {resources_path}")
                    return False
            
            # Search for the FXChain in the resource library
            fxchain_resource = None
            for bank in self._resource_library:
                # Check instruments section
                for category in bank.instruments.categories.values():
                    resource = category.get_resource(shortname)
                    if resource:
                        # Load the resource from the Python file
                        loaded_resource = resource.load_resource_from_python()
                        if loaded_resource and hasattr(loaded_resource, 'fxchain_relative_path'):
                            fxchain_resource = loaded_resource
                            break
                
                if fxchain_resource:
                    break
                    
                # Check effects section if not found in instruments
                for category in bank.effects.categories.values():
                    resource = category.get_resource(shortname)
                    if resource:
                        # Load the resource from the Python file
                        loaded_resource = resource.load_resource_from_python()
                        if loaded_resource and hasattr(loaded_resource, 'fxchain_relative_path'):
                            fxchain_resource = loaded_resource
                            break
                
                if fxchain_resource:
                    break
            
            if not fxchain_resource:
                print(f"FXChain resource '{shortname}' not found in resource library")
                return False
            
            # Get the FXChain file path
            if not fxchain_resource.fxchain_relative_path:
                print(f"FXChain resource '{shortname}' has no fxchain_relative_path defined")
                return False
            
            # Construct the source path - assume it's relative to the resource file
            source_path = resource.path.parent / fxchain_resource.fxchain_relative_path
            
            if not source_path.exists():
                print(f"FXChain file not found: {source_path}")
                return False
            
            # Copy the FXChain file to the renardo_fxchains directory
            dest_path = renardo_fxchains_dir / f"{shortname}.RfxChain"
            
            # Check if it already exists and has the same content
            if dest_path.exists():
                with open(source_path, 'rb') as src_file:
                    source_content = src_file.read()
                with open(dest_path, 'rb') as dest_file:
                    dest_content = dest_file.read()
                
                if source_content == dest_content:
                    print(f"FXChain '{shortname}' already up to date in REAPER")
                    return True
            
            # Copy the file
            import shutil
            shutil.copy2(source_path, dest_path)
            print(f"FXChain '{shortname}' installed to REAPER: {dest_path}")
            return True
            
        except Exception as e:
            print(f"Error ensuring FXChain '{shortname}' in REAPER: {e}")
            return False



@player_method
def setp(self, param_dict):
    for key, value in param_dict.items():
        setattr(self, key, value)

@player_method
def getp(self, filter = None):
    result = None
    if "reatrack" in self.attr.keys():
        reatrack = self.attr["reatrack"][0]
        if isinstance(reatrack, ReaTrack):
            #result = reatrack.config
            if filter is not None:
                result = {key: value for key, value in reatrack.get_all_params().items() if filter in key}
            else:
                result = reatrack.get_all_params()
    return result

@player_method
def showp(self, filter = None):
    pprint(self.getp(filter))