
from typing import Mapping
from pprint import pprint

from FoxDot.lib import Clock, player_method

from .ReaperInstruments import ReaperInstrumentFacade
from FoxDot.lib.Extensions.ReaperIntegrationLib.ReaProject import ReaProject
from FoxDot.lib.Extensions.ReaperIntegrationLib.ReaTrack import ReaTrack
from FoxDot.lib.Extensions.ReaperIntegrationLib.ReaTaskQueue import ReaTask

def init_reapy_project():
    project = None
    try:
        import reapy
        project = ReaProject(Clock, reapy)
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

    def update_used_track_indexes(self):
        for i in range(16):
            if len(self._reaproject.reatracks["chan"+str(i+1)].reafxs) != 0 and i+1 not in self.used_track_indexes:
                self.used_track_indexes.append(i+1)
            elif i+1 in self.used_track_indexes and len(self._reaproject.reatracks["chan"+str(i+1)].reafxs) == 0:
                self.used_track_indexes = [index for index in self.used_track_indexes if index != i+1]

    def create_instrument_facade(self, *args, **kwargs):
        """handle exceptions gracefully especially if corresponding track does not exist in Reaper"""
        try:
            return ReaperInstrumentFacade(self._reaproject, self._presets, *args, **kwargs)
        except Exception as err:
            output = err.message if hasattr(err, 'message') else err
            print("Error creating instruc {name}: {output} -> skipping".format(name=kwargs["track_name"], output=output))
            return None

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

    def add_instrument(self, name, plugin_name, track_name=None, preset=None, params={}, scan_all_params=True, is_chain=True):
        midi_channel = -1
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
        return self.create_instrument_facade(
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
    
    def add_chains(*args, scan_all_params=True, is_chain=True):
        facades = []
        # args[0] is self is the instru factory
        selff = args[0]
        for chain in args[1:]:
            try:
                facade = selff.add_instrument(chain, chain, scan_all_params=scan_all_params, is_chain=is_chain)
            except Exception as e:
                print(f"Error adding chain {chain}: {e}")
            if facade:
                facades.append(facade)
        selff.instru_facades += facades
        return tuple([facade.out for facade in facades])

    def instanciate(selff, track_name, chain_name, scan_all_params=True, is_chain=True):
        try:
            facade_obj = selff.add_instrument(chain_name, chain_name, track_name=track_name, scan_all_params=scan_all_params, is_chain=is_chain)
            return facade_obj.out
        except Exception as e:
            print(f"Error adding chain {chain_name}: {e}")
            return None

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