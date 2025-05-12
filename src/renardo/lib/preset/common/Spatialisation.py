# Pattern function
import math
from renardo.runtime import Pvar, player_method, linvar, TimeVar, var, expvar, sinvar, Pattern, xvar, yvar, P, PTri

def octo_panning_beta(value):
    value = value % 8
    # continous panning between front speakers
    output = 2
    pan = 0
    if value >= 0 and value <= 1:
        output = 2
        pan = value * 2 - 1
    # brutal jump to rear right speaker because there no way to make continuous transition
    # without left right independant volume
    elif value > 1 and value < 2:
        output = 4
        pan = -1
    # continuous panning between rear right speakers
    elif value >= 2 and value <= 3:
        output = 4
        pan = (value-2) * 2 - 1
    # brutal jump to rear left speaker because there no way to make continuous transition
    # without left right independant volume
    elif value > 3 and value < 4:
        output = 6
        pan = -1
    # continuous panning between rear left speakers
    elif value >= 4 and value <= 5:
        output = 6
        pan = (value-4) * 2 - 1
    # brutal jump to left speaker because there no way to make continuous transition
    # without left right independant volume
    elif value > 5 and value < 6:
        output = 8
        pan = -1
    # continuous panning between rear left speakers
    elif value >= 6 and value <= 7:
        output = 8
        pan = (value-6) * 2 - 1
    # brutal jump to left speaker because there no way to make continuous transition
    # without left right independant volume
    elif value > 7 and value < 6:
        output = 2
        pan = -1
    return {"output": output, "pan": pan}

def hexa_panning_beta(value):
    value = value % 6
    # continous panning between front speakers
    output = 2
    pan = 0
    if value >= 0 and value <= 1:
        output = 2
        pan = value * 2 - 1
    # brutal jump to rear right speaker because there no way to make continuous transition
    # without left right independant volume
    elif value > 1 and value < 2:
        output = 4
        pan = -1
    # continuous panning between rear right speakers
    elif value >= 2 and value <= 3:
        output = 4
        pan = (value-2) * 2 - 1
    # brutal jump to rear left speaker because there no way to make continuous transition
    # without left right independant volume
    elif value > 3 and value < 4:
        output = 6
        pan = -1
    # continuous panning between rear left speakers
    elif value >= 4 and value <= 5:
        output = 6
        pan = (value-4) * 2 - 1
    # brutal jump to left speaker because there no way to make continuous transition
    # without left right independant volume
    elif value > 5 and value < 6:
        output = 2
        pan = -1
    return {"output": output, "pan": pan}

def quadri_panning_beta(value):
    value = value % 4
    # continous panning between front speakers
    output = 2
    pan = 0
    if value >= 0 and value <= 1:
        output = 2
        pan = value * 2 - 1
    # brutal jump to rear right speaker because there no way to make continuous transition
    # without left right independant volume
    elif value > 1 and value < 2:
        output = 4
        pan = -1
    # continuous panning between rear right speakers
    elif value >= 2 and value <= 3:
        output = 4
        pan = (value-2) * 2 - 1
    # brutal jump to rear left speaker because there no way to make continuous transition
    # without left right independant volume
    elif value > 3 and value < 4:
        output = 2
        pan = -1
    return {"output": output, "pan": pan}

def hexa_panning_beta_old(value): # for interleaved speakers (less intuitive)
    value = value % 6
    # continous panning between front speakers
    output = 2
    pan = 0
    if value >= 0 and value <= 1:
        output = 2
        pan = value * 2 - 1
    # brutal jump to right speaker because there no way to make continuous transition
    # without left right independant volume
    elif value > 1 and value < 3:
        output = 4
        pan = -1
    # continuous panning between rear speakers
    elif value >= 3 and value <= 4:
        output = 6
        pan = 1 - (value - 3) * 2
    # brutal jump to left speaker because there no way to make continuous transition
    # without left right independant volume
    elif value > 4 and value < 6:
        output = 4
        pan = 1
    return {"output": output, "pan": pan}


def multi_panning_timevar_beta(entry: TimeVar, num_channels=8):
    output = 2
    pan = 0
    output_values = []
    pan_values = []
    panning_func = None
    if num_channels==8:
        panning_func = octo_panning_beta
    elif num_channels==6:
        panning_func = hexa_panning_beta
    elif num_channels==4:
        panning_func = quadri_panning_beta
    else:
        raise Exception("Num_channels should be 4,6 or 8 !")
    for value in entry.values:
        output_values.append(panning_func(value)["output"])
        pan_values.append(panning_func(value)["pan"])
        output = var(values=output_values, dur=entry.dur, start=entry.start_time)
    if isinstance(entry, linvar):
        pan = linvar(values=pan_values, dur=entry.dur, start=entry.start_time)
    elif isinstance(entry, sinvar):
        pan = sinvar(values=pan_values, dur=entry.dur, start=entry.start_time)
    elif isinstance(entry, expvar):
        pan = expvar(values=pan_values, dur=entry.dur, start=entry.start_time)
    elif isinstance(entry, TimeVar) and not isinstance(entry, Pvar):
        pan = var(values=pan_values, dur=entry.dur, start=entry.start_time)
    return {"output": output, "pan": pan}

def multi_panning_simple_pattern(entry: Pattern, num_channels=8):
    panning_func = None
    if num_channels==8:
        panning_func = octo_panning_beta
    elif num_channels==6:
        panning_func = hexa_panning_beta
    elif num_channels==4:
        panning_func = quadri_panning_beta
    else:
        raise Exception("Num_channels should be 4,6 or 8 !")
    output_pattern = []
    pan_pattern = []
    for value in entry:
        output_pattern.append(panning_func(value)["output"])
        pan_pattern.append(panning_func(value)["pan"])
    result = {"output": output_pattern, "pan": pan_pattern}
    return result

@player_method
def mpan(self, entry, num_channels=8):
    if isinstance(entry, TimeVar):
        res = multi_panning_timevar_beta(entry, num_channels=num_channels)
        self.pan = res["pan"]
        self.output = res["output"]
        return self
    elif not hasattr(entry, '__iter__') or isinstance(entry, tuple):
        entry = Pattern(entry)
    res = multi_panning_simple_pattern(entry, num_channels=num_channels)
    self.pan = res["pan"]
    self.output = res["output"]
    return self

def surround_panning(position=0, distance=1, num_channels=8):
    if num_channels == 8:
        init_offset = 5.5
    elif num_channels == 6:
        init_offset = 4
    elif num_channels == 4:
        init_offset = 2.5
    else:
        raise Exception("Num_channels should be 4,6 or 8 !")
    position = (position + init_offset) % num_channels  # first speaker is at 240 degree (fifth speaker => 4 counting from 0)
    degree = -1 * position / float(num_channels) * 360
    surx = math.cos(math.radians(degree))
    sury = math.sin(math.radians(degree))
    # the circle is at center .5/.5 and r = distance/2
    sury = distance * 1 / 2 * sury + .5
    surx = distance * 1 / 2 * surx + .5
    return {"sur_x": surx, "sur_y": sury}

def surpan(position, distance=1, num_channels=8):
    if isinstance(position, linvar):
        values = [ (value % num_channels) * 360 / num_channels for value in position.values ]
        print(values)
        surx = xvar(values=values, dur=position.dur, start=position.start_time)
        sury = yvar(values=values, dur=position.dur, start=position.start_time)
        sury = distance * 1 / 2 * sury + .5
        surx = distance * 1 / 2 * surx + .5
    elif isinstance(position, TimeVar):
        xy_values = [surround_panning(pos, distance, num_channels=num_channels) for pos in position.values]
        surx = var(values=[elem["sur_x"] for elem in xy_values], dur=position.dur, start=position.start_time)
        sury = var(values=[elem["sur_y"] for elem in xy_values], dur=position.dur, start=position.start_time)
    else:
        surx = surround_panning(position, distance, num_channels=num_channels)["sur_x"]
        sury = surround_panning(position, distance, num_channels=num_channels)["sur_y"]
    return {"sur_x": surx, "sur_y": sury}

@player_method
def span(self, position, distance=1, num_channels=8):
    res = surpan(position, distance, num_channels=num_channels)
    self.sur_x = res["sur_x"]
    self.sur_y = res["sur_y"]
    return self

# panning rotation using linvar for use with span method
def srot(duration=16, num_channels=8):
    if isinstance(duration, int):
        return  linvar(P[0, .99]*num_channels, [duration, 0])
    elif isinstance(duration, (Pattern, list)):
        return linvar(P[0, .99]*num_channels, [duration, 0])

# panning rotation using pattern rather than vars for use with mpan
def mrot(duration=16, num_channels=8):
    if isinstance(duration, int):
        return P[range(duration)]/duration*num_channels
    elif isinstance(duration, (Pattern, list)):
        return PTri(duration)/sum(duration)*num_channels

