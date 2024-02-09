from typing import Tuple, Optional, Union

from FoxDot.lib.TimeVar import TimeVar
from FoxDot.lib.Patterns import Pattern
from .ReaFX import ReaFX, ReaFXGroup
from .ReaParam import ReaParamState
from .ReaTrack import ReaTrack
from .ReaTaskQueue import TaskQueue, ReaTask
from .ReaTrack import ReaTrackType
from .functions import make_snake_name, split_param_name


class ReaProject(object):
    def __init__(self, clock, reapylib):
        self._clock = clock
        self.reapy_project = reapylib.Project()
        self.reatracks = {}
        self.reapylib = reapylib
        self.name = self.reapy_project.name
        self.instrument_tracks = []
        self.bus_tracks = []
        self.task_queue = TaskQueue(clock, reapylib)
        self.init_reaproject()

    def __repr__(self):
        return "<ReaProject \n\n ################ \n\n {}>".format(self.reatracks)

    def get_track(self, track_name):
        return self.reatracks[track_name]

    def init_reaproject(self):
        if self.reatracks == {}:
            with self.reapylib.inside_reaper():
                for index, track in enumerate(self.reapy_project.tracks):
                    snake_name: str = make_snake_name(track.name)
                    reatrack = ReaTrack(self._clock, track, name=snake_name, type=ReaTrackType.INSTRUMENT, reaproject=self)
                    self.reatracks[snake_name] = reatrack
                    if snake_name.startswith('_'):
                        self.bus_tracks.append(reatrack)
                    else:
                        self.instrument_tracks.append(reatrack)
            self.task_queue.set_active()
        else:
            print("ReaProject Already initialized. skipping")

    def update_reaproject(self, shallow=True):
        self.task_queue.set_inactive()
        contextt = self.reapylib.is_inside_reaper()
        with self.reapylib.inside_reaper():
            new_reatrack_dict = {}
            for index, track in enumerate(self.reapy_project.tracks):
                snake_name: str = make_snake_name(track.name)
                if snake_name in self.reatracks.keys():
                    self.reatracks[snake_name].update_reatrack(shallow)
                    new_reatrack_dict[snake_name] = self.reatracks[snake_name]
                else:
                    new_reatrack_dict[snake_name] = ReaTrack(self._clock, track, name=snake_name, type=ReaTrackType.INSTRUMENT, reaproject=self)
            self.reatracks = new_reatrack_dict
        self.task_queue.set_active()


def get_reaper_object_and_param_name(track: ReaTrack, param_fullname: str, quiet: bool = True)\
        -> Tuple[Optional[Union[ReaTrack, ReaFX]], Optional[str]]:
    """
    Return object (ReaTrack or ReaFX) and parameter name to apply modification to.
    Choose usecase (parameter kind : track param like vol, send amount or fx param) depending on parameter name.
    """
    reaper_object, param_name = None, None
    # Param concern current track (it is a reaper send)
    if param_fullname in track.reaparams.keys():
        reaper_object = track
        return reaper_object, param_fullname
    # Try to find param in the first fx (instrument)
    elif (
        track.firstfx is not None and
        param_fullname in track.reafxs[track.firstfx].reaparams.keys()
    ):
        reaper_object = track.reafxs[track.firstfx]
        return reaper_object, param_fullname
    # Param is a fully qualified fx param example darkpass_rm
    elif '_' in param_fullname:
        fx_name, rest = split_param_name(param_fullname)
        if fx_name in track.reafxs.keys():
            fx = track.reafxs[fx_name]
            if rest in fx.reaparams.keys() or rest == 'on':
                reaper_object = track.reafxs[fx_name]
                param_name = rest
                return reaper_object, param_name
    if not quiet:
        print("Parameter doesn't exist: " + param_fullname)
    return reaper_object, param_name


def set_reaper_param(track: ReaTrack, full_name, value, update_freq=.1):
    # rea_object can point to a fx or a track (self) -> (when param is vol or other send)
    rea_object, name = get_reaper_object_and_param_name(track, full_name)

    # If object not found abort
    if rea_object is None or name is None:
        return

    # If we set an fx param turn the fx on
    if isinstance(rea_object, ReaFX) or isinstance(rea_object, ReaFXGroup):
        if name != 'on':
            track.reaproject.task_queue.add_task(ReaTask("set", rea_object, 'on', True))

    # handle switching between time varying (setup recursion loop to update value in the future) or non varying params (normal float)
    if isinstance(value, TimeVar) and name != 'on':
        # to update a time varying param and tell the preceding recursion loop to stop
        # we switch between two timevar state old and new alternatively 'timevar1' and 'timevar2'
        if rea_object.reaparams[name].state != ReaParamState.VAR1:
            new_state = ReaParamState.VAR1
        else:
            new_state = ReaParamState.VAR2
        def initiate_timevar_update_loop(name, value, new_state, update_freq):
            rea_object.reaparams[name].state = new_state
            track.reaproject.task_queue.timevar_update_loop(rea_object, name, value, new_state, update_freq)
        # beat_count=None means schedule for the next bar
        track._clock.schedule(initiate_timevar_update_loop, beat_count=None, args=[name, value, new_state, update_freq])
    else:
        # to switch back to non varying value use the state normal to make the recursion loop stop
        def normal_value_update(rea_object, name, value):
            rea_object.reaparams[name].state = ReaParamState.NORMAL
            try:
                rea_object.set_param(name, float(value))
                track.reaproject.task_queue.add_task(ReaTask("set", rea_object, name, float(value)))
            except:
                print(f'Failure doing a normal value update from {name} with {value} of type {type(value)}')
                # if isinstance(value, Pattern):
                #     print('Trying update with first element of the pattern !')
                #     try:
                #         value = value[0]
                #         rea_object.set_param(name, float(value))
                #         track.reaproject.task_queue.add_task(ReaTask("set", rea_object, name, float(value)))
                #     except:
                #         print("Failed again")

        # beat_count=None means schedule for the next bar
        track._clock.schedule(normal_value_update, beat_count=None, args=[rea_object, name, value])


def get_reaper_param(reaobject, full_name):
    # rea_object can point to a fx or a track (self) -> (when param is vol or pan)
    rea_object, name = get_reaper_object_and_param_name(reaobject, full_name)
    if rea_object is None or name is None:
        return None
    return rea_object.get_param(full_name)
