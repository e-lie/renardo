from enum import Enum
from pprint import pformat
from typing import Dict

from .ReaFX import ReaFX, ReaFXGroup
from .ReaParam import ReaSend
from .functions import make_snake_name, split_param_name

class ReaTrackType(Enum):
    INSTRUMENT = 1
    BUS = 2

class ReaTrack(object):
    def __init__(self, clock, track, name: str, type: ReaTrackType, reaproject):
        self._clock = clock
        self.track = track
        self.reaproject = reaproject
        self.name = name
        self.type = type
        self.reafxs = {}
        self.firstfx = None
        self.preset = None
        self.reaparams: Dict[str, ReaSend] = {}
        self.init_reatrack()

    def init_reatrack(self):
        for index, send in enumerate(self.track.sends):
            name = make_snake_name(send.dest_track.name)#[1:] # to remove the _ of bux track name
            if index == 0:
                self.reaparams["vol"] = ReaSend(name=name, index=index, value=send.volume*2)
                pass
            else:
                self.reaparams[name] = ReaSend(name=name, index=index, value=send.volume)

        preceding_fx_name = None
        for index, fx in enumerate(self.track.fxs):
            snake_name = make_snake_name(fx.name)
            if index == 0 and self.firstfx is None:
               self.firstfx = snake_name
            if snake_name != preceding_fx_name: # if preceding fx has same name, it's a group
                if snake_name not in self.reafxs.keys():
                    reafx = ReaFX(fx, snake_name, index)
                    self.reafxs[snake_name] = reafx
            else: # if it's a group
                if isinstance(self.reafxs[snake_name], ReaFXGroup): # already a group (at least two instances) add a new instance
                    self.reafxs[snake_name].add_fx_to_group(fx, index)
                else:
                    self.replace_fx_with_fxgroup_in_dict(self.reafxs, index, snake_name, fx) # if not replace fx with a group of two instances
            preceding_fx_name = snake_name

    def replace_fx_with_fxgroup_in_dict(self, fx_dict, index, snake_name, fx):
        old_reafx = fx_dict[snake_name]
        fx_dict[snake_name] = ReaFXGroup([old_reafx.fx, fx], snake_name, [old_reafx.index, index])

    def update_reatrack(self, shallow=True):
        new_reaparams_dict = {}
        new_reafxs_dict = {}

        for index, send in enumerate(self.track.sends):
            name = make_snake_name(send.dest_track.name)#[1:]
            if name == "chan1":
                if "vol" not in self.reaparams.keys():
                    new_reaparams_dict["vol"] = ReaSend(name=name, index=index, value=send.volume * 2)
                else:
                    new_reaparams_dict["vol"] = self.reaparams["vol"]
            else:
                if name not in self.reaparams.keys():
                    new_reaparams_dict[name] = ReaSend(name=name, index=index, value=send.volume)
                else:
                    new_reaparams_dict[name] = self.reaparams[name] # if reaparam exist do nothing (param value won't be updated as it is not supposed to be touched manually nor read from foxdot)
        self.reaparams = new_reaparams_dict

        preceding_fx_name = None
        for index, fx in enumerate(self.track.fxs):
            snake_name = make_snake_name(fx.name)
            #if index == 0 and self.firstfx is None:
            #    self.firstfx = snake_name
            if snake_name != preceding_fx_name: # if preceding fx has same name, it's a group
                if snake_name in self.reafxs.keys():
                    new_reafxs_dict[snake_name] = self.reafxs[snake_name]
                else:
                    new_reafxs_dict[snake_name] = ReaFX(fx, snake_name, index)
            else:
                if isinstance(new_reafxs_dict[snake_name], ReaFXGroup):
                    if index not in new_reafxs_dict[snake_name].indexes: # the case when a new fxgroup appear at update time and has to be filled with several fx instances
                        new_reafxs_dict[snake_name].add_fx_to_group(fx, index)
                    else:
                        pass # if current fx is part of the group, we are in an update case => nothing to do because fxgroup has already been updated juste before
                else: # case where we add the second instance to a
                    self.replace_fx_with_fxgroup_in_dict(new_reafxs_dict, index, snake_name, fx)
            preceding_fx_name = snake_name
            self.reafxs = new_reafxs_dict

    def __repr__(self):
        return "<ReaTrack {} - {}>".format(self.name, pformat(self.reafxs))


    # def create_reafx(self, plugin_name: str, plugin_preset: str=None, reafx_name: str=None, param_alias_dict={}, scan_all_params=False):
    #     def add_fx_plugin_with_preset(self, plugin_name, plugin_preset):
    #         if not self.reafxs and self.firstfx is None:
    #             self.firstfx = reafx_name
    #         # add fx in last position : the index is len of the fx list - 1
    #         fx = self.track.add_fx(plugin_name)
    #         if plugin_preset is not None:  # plugin preset in reaper has to be applied first (before ReaFX obj creation) as it changes existing parameters
    #             fx.preset = plugin_preset
    #             self.preset = plugin_preset
    #         return fx
        
    #     if reafx_name is None:
    #         reafx_name = make_snake_name(plugin_name)
    #     fx = None
    #     reafx = None
    #     with self.reaproject.reapylib.inside_reaper():
    #         fx = add_fx_plugin_with_preset(self, plugin_name, plugin_preset)
    #         reafx = ReaFX(fx, reafx_name, len(self.reafxs.keys()) - 1, param_alias_dict, scan_all_params)
    #     self.reafxs[reafx_name] = reafx
    #     return reafx


    def create_reafxs_for_chain(self, chain_name, param_alias_dict={}, scan_all_params=False):
        fx_count = 1
        chain_reafx_names = []
        with self.reaproject.reapylib.inside_reaper():
            fx_count = self.reaproject.add_fx_chain(self.track, chain_name)
        # iterate over the last fx_count fxs on track to instanciate reafxs as they are the chain fxs
            for fx in self.track.fxs[len(self.track.fxs) - fx_count:]:
                reafx_name = make_snake_name(fx.name)
                if not self.reafxs and self.firstfx is None:
                    self.firstfx = reafx_name
                reafx = ReaFX(fx, reafx_name, len(self.reafxs.keys()) - 1, param_alias_dict, scan_all_params)
                self.reafxs[reafx_name] = reafx
                chain_reafx_names.append(reafx_name)
        return chain_reafx_names


    def delete_reafx(self, fx_index, reafx_name):
        self.track.fxs[fx_index].delete()
        del self.reafxs[reafx_name]

    def get_param(self, full_name):
        if full_name in self.reaparams.keys():
            return self.reaparams[full_name].value
        else:
            fx_name, param_name = split_param_name(full_name)
            return self.reafxs[fx_name].reaparams[param_name].value

    def get_all_params(self):
        result = {send.name: send.value for send in self.reaparams.values()}
        for reafx in self.reafxs.values():
            result = result | reafx.get_all_params()
        return result

    def set_param(self, name, value):
        # if name == "mixer":
        #     name = "vol"
        # name = "vol" if name =="mixer" else name
        # value = value/2 if name =="vol" else value
        self.reaparams[name].value = value

    def set_param_direct(self, name, value):
        value = value/2 if name =="vol" else value
        param = self.reaparams[name]
        self.track.sends[param.index].volume = 5*float(value)**2.5 # convert vol logarithmic value to linear 0 -> 1 value


