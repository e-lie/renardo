from typing import Dict, List

from .ReaParam import ReaParam
from .functions import make_snake_name


class ReaFX(object):
    def __init__(self, fx, name, index, param_alias_dict={}, scan_all_params=True):
        self.fx = fx
        self.name = name
        self.index = index
        self.reaparams: Dict[str, ReaParam] = {}
        self.param_alias_dict = param_alias_dict
        self.scan_all_params = scan_all_params
        self.init_params()

    def init_params(self):
        self.reaparams['on'] = ReaParam(name='on', value=self.fx.is_enabled, index=-1)
        if self.scan_all_params:
            for index, param in enumerate(self.fx.params):
                #print(f"reafx {self.name}: param num {index}")
                if param.name in self.param_alias_dict.keys():
                    param_alias = make_snake_name(self.param_alias_dict[param.name])
                    param_reaper_name = param.name
                else:
                    param_alias = make_snake_name(param.name)
                    param_reaper_name = param.name
                self.reaparams[param_alias] = ReaParam(name=param_alias, value=param.real, index=index, reaper_name=param_reaper_name)
        else:
            for param_name in self.param_alias_dict.keys():
            #selected_params = [param for param in fx.params if param.name in param_alias_dict.keys()]
            #for index, param in enumerate(selected_params):
                try:
                    #param_name = param.name
                    param = self.fx.params[param_name]
                    #if param_name in param_alias_dict.keys():
                    param_alias = make_snake_name(self.param_alias_dict[param_name])
                    param_reaper_name = param.name
                    self.reaparams[param_alias] = ReaParam(name=param_alias, value=param.real, index=param.index,
                                                           reaper_name=param_reaper_name)
                except:
                    print(f"Param with name {param_name} does not exist in Reaper FX {self.name}")
                    print(f"Existing params : {[param.name for param in self.fx.params]}")

    def update_params(self):
        for reaparam in self.reaparams.values():
            reaparam.update()


    def __repr__(self):
        return "<ReaFX {}>".format(self.name)

    def get_all_params(self):
        return {self.name + "_" + param.name : param.value for param in self.reaparams.values()}

    def get_param(self, name):
        return self.reaparams[name].value

    def set_param(self, name, value):
        self.reaparams[name].value = value

#    def set_param_direct(self, name, value):
#        if name == "on":
#            if not value:
#                self.fx.disable()
#            else:
#                self.fx.enable()
#        else:
#            reaper_name = self.reaparams[name].reaper_name
#            try:
#                self.fx.params[reaper_name] = float(value)
#                print(f"set param direct: {name} {reaper_name} {value}")
#            except:
#                print(f"error set param direct: {name} {reaper_name} {value}")


    def set_param_direct(self, name, value):
        if name == "on":
            if not value:
                self.fx.disable()
            else:
                self.fx.enable()
        else:
            id = self.reaparams[name].index
            try:
                self.fx.params[id] = float(value)
            except:
                print(f"reafx {self.name} doesn't seem to work anymore")


class ReaFXGroup(ReaFX):
    def __init__(self, fxs, name, indexes:List[int]):
        self.fxs = fxs
        self.name = name
        self.indexes = indexes
        self.reaparams: Dict[str, ReaParam] = {}
        self.reaparams['on'] = ReaParam(name='on', value=fxs[0].is_enabled, index=-1)
        for index, param in enumerate(fxs[0].params):
            snake_name = make_snake_name(param.name)
            self.reaparams[snake_name] = ReaParam(name=snake_name, value=param.real, index=index)

    def add_fx_to_group(self, fx, index):
        self.fxs.append(fx)
        self.indexes.append(index)

    def __repr__(self):
        return "<ReaFXGroup {}>".format(self.name)

    def set_param_direct(self, name, value):
        if name == "on":
            for fx in self.fxs:
                if not value:
                    fx.disable()
                else:
                    fx.enable()
        else:
            id = self.reaparams[name].index
            for fx in self.fxs:
                try:
                    fx.params[id] = float(value)
                except:
                    print(f"reafx {self.name} doesn't seem to work anymore")
