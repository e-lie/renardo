# Pattern function
from copy import Error

import math
from renardo.runtime import Pvar, Pattern, PEuclid, P

def groove_rythm_combination(rythm, groove):
    """
    b1 >> blip(0, dur=grc([2,1,2,2,3], [.4,.3,.3]))
    b1 >> blip(0, dur=grc([2,1,2,2,3], P[.4,.3,.3] << [0,0.02,0]))
    """
    rythm = list(rythm)
    groove = list(groove)
    dur_sum = sum(rythm)
    lcm = math.lcm(len(groove), dur_sum)
    groove *= lcm // len(groove)
    rythm *= lcm // dur_sum
    res = []
    index = 0
    # print(f"{rythm} - {dur_sum}")
    while True:
        # print(f"len ry:{len(rythm)} len gro:{len(groove)}")
        if len(groove) == 0:
            break
        current_rythm = rythm[index%len(rythm)]
        current_dur = 0
        for i in range(current_rythm):
            current_dur += groove.pop(0)
        index += 1
        res.append(current_dur)
    # print(res)
    return res

grc = groove_rythm_combination

def PEu(nb_strokes, total, shift=0, base_dur=.5):
    """
    alternative euclidian rythms functions
    """
    res = []
    accu = 0
    Peu = PEuclid(nb_strokes, total)
    for e in Peu[1:]|Peu[0]:
        accu += base_dur
        if e == 1:
            res.append(accu)
            accu = 0
    if shift > 0:
        res = [Rest(base_dur*shift)]+res[:shift]+res[:-shift]
        res[-1] -= base_dur
    return P[res]

def pattern_interpolation(start, end, step=7, go_back=False):
    if len(start) == 1 and len(end) > 1:
        start = [start[0]] * len(end)
    if len(end) == 1 and len(start) > 1:
        end = [end[0]] * len(start)
    assert len(start) == len(end)
    diffs = []
    result = []
    for i in range(len(start)):
        diffs += [start[i] - end[i]]
    base_pattern = start
    for j in range(step):
        new_pattern = [
            e - diffs[k]/(step + 1) for k, e in enumerate(base_pattern)
        ]
        result.append(new_pattern)
        base_pattern = new_pattern
    if not go_back:
        result = [start] + result + [end]
    else:
        result = (
            [start] + result + [end] + FadingFunctionsresult[::-1]
        )  # result except last elem + end + reversed result
    return result

def Pvar_interpolation(start, end, total_dur=None, step=6, dur=1, go_back=False):
    """
    return a Pvar object interpolating patterns (meant for rythms)

    bb >> blip([0,2,1], dur=Pvi([.5,.25,.25], [1/3]))    
    """
    if total_dur is not None:
        step = (total_dur - 2) // 2
        dur = 1
    return Pvar(pattern_interpolation(start, end, step, go_back), dur)

Pvi = Pvar_interpolation

def P_interpolation(start, end, repeat=1, step=6):
    """
    return a Pattern concatenation of all the pattern of a pattern interpolation

    bb >> blip([0,1,2], dur=Pi([.5,.25,.25]))
    """
    res = Pattern([])
    for pattern in pattern_interpolation(start, end, step, go_back=True):
        for i in range(repeat):
            res = res | pattern
    return res

Pi = P_interpolation

# def interPBof2(start, end, repeat=1, step=6, go_back=True):
#     res = Pattern([])
#     for pattern in pattern_interpolation(start, end, step, go_back):
#         for i in range(repeat):
#             res = res | pattern
#     pprint(res)
#     if not go_back:
#         for i in range(10):
#             res = res | Pattern(end)
#         total_dur = sum(res)
#         print(total_dur)
#         return Pvar([res, end], [int(total_dur)-1, inf], start=Clock.mod(4))
#     else:
#         return res

# def interPBof(start, end, step=6, total_dur=None,  dur=4, go_back=False):
#     if total_dur is not None:
#         step = (total_dur - 2) // 2
#         dur = 4
#     patterns = interpolate(start, end, step, go_back)
#     if not go_back:
#         res = Pvar(patterns, [dur]*(len(patterns)-1) + [inf], start=Clock.now())
#     else:
#         res = Pvar(patterns, [dur], start=Clock.now())
#     return res

def microshift(pattern, shifts):
    for key, value in shifts.items():
        if key in range(len(pattern) - 1):
            pattern[key] += value
            pattern[key + 1] -= value
    print(pattern)
    return pattern
