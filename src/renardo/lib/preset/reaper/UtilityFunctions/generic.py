from renardo.lib.runtime import PWhite, inf, Clock, linvar, player_method

def randomize_settings(param_dict, seed=0):
    params_values = PWhite(seed=seed)[:len(param_dict.keys())]
    result = {}
    for i, key in enumerate(param_dict.keys()):
        result[key] = params_values[i]
    return result

rnds = randomize_settings



def interpolate_settings(param_dict1, param_dict2, duration):
    result = {}
    assert param_dict1.keys() == param_dict2.keys()
    for key, value in param_dict1.items():
       if param_dict1[key] != param_dict2[key]:
           result[key] = linvar([param_dict1[key], param_dict2[key]], [duration, inf], start=Clock.mod(4))
    return result

inters = interpolate_settings

@player_method
def tos(self, param_dict, duration):
    if "reatrack" in self.attr.keys() and isinstance(self.attr["smart_track"][0], SmartTrack):
        init_params = {}
        for key, value in param_dict.items():
            init_params[key] = getattr(self, key)
        self.setp(interpolate_settings(init_params, param_dict, duration))
