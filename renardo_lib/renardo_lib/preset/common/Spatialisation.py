# Pattern function
from copy import Error

import math
from FoxDot import Player, Group, Pvar, player_method, PWhite, linvar, inf, Clock, TimeVar, var, expvar, sinvar, Pattern, xvar, yvar, P


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

def hexa_panning_timevar_beta(entry: TimeVar):
    output = 2
    pan = 0
    output_values = []
    pan_values = []
    for value in entry.values:
        output_values.append(hexa_panning_beta(value)["output"])
        pan_values.append(hexa_panning_beta(value)["pan"])
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

def quadri_panning_timevar_beta(entry: TimeVar):
    output = 2
    pan = 0
    output_values = []
    pan_values = []
    for value in entry.values:
        output_values.append(quadri_panning_beta(value)["output"])
        pan_values.append(quadri_panning_beta(value)["pan"])
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

def hexa_panning_simple_pattern(entry: Pattern):
    output_pattern = []
    pan_pattern = []
    for value in entry:
        output_pattern.append(hexa_panning_beta(value)["output"])
        pan_pattern.append(hexa_panning_beta(value)["pan"])
    result = {"output": output_pattern, "pan": pan_pattern}
    return result

def quadri_panning_simple_pattern(entry: Pattern):
    output_pattern = []
    pan_pattern = []
    for value in entry:
        output_pattern.append(quadri_panning_beta(value)["output"])
        pan_pattern.append(quadri_panning_beta(value)["pan"])
    result = {"output": output_pattern, "pan": pan_pattern}
    return result

@player_method
def mpan(self, entry):
    if isinstance(entry, TimeVar):
        res = quadri_panning_timevar_beta(entry)
        self.pan = res["pan"]
        self.output = res["output"]
        return self
    elif not hasattr(entry, '__iter__') or isinstance(entry, tuple):
        entry = Pattern(entry)
    res = quadri_panning_simple_pattern(entry)
    self.pan = res["pan"]
    self.output = res["output"]
    return self

def mpan(entry):
    if isinstance(entry, TimeVar):
        return hexa_panning_timevar_beta(entry)
    elif not hasattr(entry, '__iter__') or isinstance(entry, tuple):
        entry = Pattern(entry)
    return hexa_panning_simple_pattern(entry)


def surround_panning_6(position=0, distance=1):
    position = (position + 4) % 6  # first speaker is at 240 degree (fifth speaker => 4 counting from 0)
    degree = -1 * position / 6.0 * 360
    surx = math.cos(math.radians(degree))
    sury = math.sin(math.radians(degree))
    # the circle is at center .5/.5 and r = distance/2
    sury = distance * 1 / 2 * sury + .5
    surx = distance * 1 / 2 * surx + .5
    return {"sur_x": surx, "sur_y": sury}

def surround_panning_4(position=0, distance=1):
    position = (position + 2.5) % 4  # first speaker is at 240 degree (fifth speaker => 4 counting from 0)
    degree = -1 * position / 4.0 * 360
    surx = math.cos(math.radians(degree))
    sury = math.sin(math.radians(degree))
    # the circle is at center .5/.5 and r = distance/2
    sury = distance * 1 / 2 * sury + .5
    surx = distance * 1 / 2 * surx + .5
    return {"sur_x": surx, "sur_y": sury}


def surpan6(position, distance=1):
    if isinstance(position, linvar):
        values = [ (value % 6) * 60 for value in position.values ]
        print(values)
        surx = xvar(values=values, dur=position.dur, start=position.start_time)
        sury = yvar(values=values, dur=position.dur, start=position.start_time)
        sury = distance * 1 / 2 * sury + .5
        surx = distance * 1 / 2 * surx + .5
    elif isinstance(position, TimeVar):
        xy_values = [surround_panning_6(pos, distance) for pos in position.values]
        surx = var(values=[elem["sur_x"] for elem in xy_values], dur=position.dur, start=position.start_time)
        sury = var(values=[elem["sur_y"] for elem in xy_values], dur=position.dur, start=position.start_time)
    else:
        surx = surround_panning_6(position, distance)["sur_x"]
        sury = surround_panning_6(position, distance)["sur_y"]
    return {"sur_x": surx, "sur_y": sury}

def surpan4(position, distance=1):
    if isinstance(position, linvar):
        values = [ (value % 4) * 90 for value in position.values ]
        print(values)
        surx = xvar(values=values, dur=position.dur, start=position.start_time)
        sury = yvar(values=values, dur=position.dur, start=position.start_time)
        sury = distance * 1 / 2 * sury + .5
        surx = distance * 1 / 2 * surx + .5
    elif isinstance(position, TimeVar):
        xy_values = [surround_panning_4(pos, distance) for pos in position.values]
        surx = var(values=[elem["sur_x"] for elem in xy_values], dur=position.dur, start=position.start_time)
        sury = var(values=[elem["sur_y"] for elem in xy_values], dur=position.dur, start=position.start_time)
    else:
        surx = surround_panning_4(position, distance)["sur_x"]
        sury = surround_panning_4(position, distance)["sur_y"]
    return {"sur_x": surx, "sur_y": sury}

@player_method
def span(self, position, distance=1):
    res = surpan4(position, distance)
    self.sur_x = res["sur_x"]
    self.sur_y = res["sur_y"]
    return self


base_mpan_dict = {
    0: {
        "output": 2,
        "pan": -1
    },
    1: {
        "output": 2,
        "pan": 1
    },
    2: {
        "output": 4,
        "pan": -1
    },
    3: {
        "output": 6,
        "pan": 1
    },
    4: {
        "output": 6,
        "pan": -1
    },
    5: {
        "output": 4,
        "pan": 1
    },
}

def surotate(dur=4):
    sury = sinvar([0,1], 4)
    return {"sur_x": 1, "sur_y": 1}
    
# panning rotation using linvar for use with span method
def srot(duration=16, number_of_channels=4):
    if isinstance(duration, int):
        return  linvar(P[0, .99]*number_of_channels, [duration, 0])
    elif isinstance(duration, (Pattern, list)):
        return linvar(P[0, .99]*number_of_channels, [duration, 0])

# panning rotation using pattern rather than vars for use with mpan
def mrot(duration=16, number_of_channels=4):
    if isinstance(duration, int):
        return P[range(duration)]/duration*number_of_channels
    elif isinstance(duration, (Pattern, list)):
        return PTri(duration)/sum(duration)*number_of_channels

