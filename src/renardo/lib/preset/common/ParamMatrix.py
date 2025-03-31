from renardo.lib.runtime import Pvar
from typing import List


class ParamRange:

    def __init__(self, start, stop, value):
        print(start, stop)
        assert start < stop, "A param range should have start < stop"
        self.start = start
        self.stop = stop
        self.value = value

    def __repr__(self):
        return f"<ParamRange {self.start} {self.stop} - {self.value}>"

    def __eq__(self, other):
        return self.start == other.start and self.stop == other.stop

    def __lt__(self, other): # to make it sortable
        return self.start < other.start

    def __hash__(self):
        return hash((self.start, self.stop, self.value))

    def overlap(self, other):
        disjoint_1 = self.start < other.start and self.stop <= other.start
        disjoint_2 = other.start < self.start and other.stop <= self.start
        return not (disjoint_1 or disjoint_2)

    def boolean_union(self, other):
        assert self.overlap(other), "Ranges should overlap to execute boolean operation"
        if self.start >= other.start and other.stop >= self.stop:
            return [ParamRange(other.start, other.stop, other.value)]
        elif self.start < other.start and self.stop <= other.stop:
            return [
                ParamRange(self.start, other.start, self.value),
                ParamRange(other.start, other.stop, other.value)
            ]
        elif self.start < other.start and self.stop > other.stop:
            return [
                ParamRange(self.start, other.start, self.value),
                ParamRange(other.start, other.stop, other.value),
                ParamRange(other.stop, self.stop, self.value),
            ]
        elif other.start <= self.start and other.stop < self.stop:
            return [
                ParamRange(other.start, other.stop, other.value),
                ParamRange(other.stop, self.stop, self.value),
            ]
        elif self.stop == other.start:
            return [
                ParamRange(self.start, self.stop, self.value),
                ParamRange(other.start, other.stop, other.value)
            ]
        elif self.start == other.stop:
            return [
                ParamRange(other.start, other.stop, other.value),
                ParamRange(self.start, self.stop, self.value),
            ]
        else:
            raise Exception("Error in ParamRange boolean operation")

def uniq(l:List):
    res = []
    for x in l:
        if x not in res:
            res.append(x)
    return res

class ParamTimeline:

    def __init__(self, duration, value):
        self.base = value
        self.param_ranges = [ParamRange(0, duration, value)]
        self.duration = duration

    def add_value_range(self, new_pr: ParamRange):
        assert new_pr.start >= 0 and new_pr.stop <= self.duration, "new range should be inside total timeline range"
        new_param_ranges = []
        for pr in self.param_ranges:
            if pr.overlap(new_pr):
                new_param_ranges += pr.boolean_union(new_pr)
            else:
                new_param_ranges.append(pr)
        new_param_ranges = uniq(new_param_ranges)
        new_param_ranges.sort()
        self.param_ranges = new_param_ranges
        for i, pr in enumerate(self.param_ranges): # merge Param Ranges contiguous with same value by overwriting with a new PR
            if i < len(self.param_ranges)-1:
                if self.param_ranges[i].value == self.param_ranges[i+1].value:
                    self.add_value_range(ParamRange(self.param_ranges[i].start, self.param_ranges[i+1].stop, self.param_ranges[i].value))
        return self
    def __lshift__(self, other):
        assert isinstance(other, tuple) and len(other) == 3, "lshift operator for param timeline works with tuples of length 3"
        self.add_value_range(ParamRange(other[0], other[1], other[2]))
        return self
    def __mul__(self, other):
        if isinstance(other, int):
            old_duration = self.duration
            self.duration *= other
            for i in range(1,other):
                for pr in self.param_ranges:
                    new_pr = ParamRange(
                        start=pr.start + i*old_duration,
                        stop=pr.stop + i*old_duration,
                        value=pr.value,
                    )
                    self.add_value_range(new_pr)
        return self
    def __repr__(self):
        return f"<ParamTimeline {self.param_ranges}>"

    def out(self):
        if len(self.param_ranges) == 1:
            return self.param_ranges[0].value
        values = [pr.value for pr in self.param_ranges]
        durations = [pr.stop - pr.start for pr in self.param_ranges]
        return Pvar(values, durations)



Pt = ParamTimeline


class ParamMatrix:
    def __init__(self, duration, *args, **kwargs):
        self.duration = duration
        # self.params = { # default values
        #     "degree": P[0],
        #     "dur": P[1],
        #     "amp": P[1],
        # }
        # problem with default values in matrix is that it blocks the usage of manual params in addition to the matrix
        self.params = { key: ParamTimeline(duration, value) for key, value in kwargs.items() }
        # self.params["sus"] = self.params["dur"] if 'sus' not in self.params.keys() else self.params["sus"]
    def __lshift__(self, other):
        assert isinstance(other, ParamVector), "lshift operator for param matrix works with a ParamVector"
        for key, value in other.params.items():
            if key in self.params.keys():
                start = other.start if other.start is not None else 0
                stop = other.stop if other.stop is not None else self.duration
                self.params[key].add_value_range(ParamRange(
                    start,
                    stop,
                    value
                ))
            else: # if the param does not exist in matrix (no value nor default value) add its value to the whole timeline
                self.params[key] = ParamTimeline(self.duration, value)
        return self
    def __mul__(self, other):
        if isinstance(other, int):
            self.duration = self.duration * other
            for key, value in self.params.items():
                res = value * other
                self.params[key] = res
        return self
    def __repr__(self):
        return f"<ParamMatrix { { key:value for key, value in self.params.items()} }>"
    def out(self):
        res = { key: _pt.out() for key, _pt in self.params.items() }
        return res
Pm = ParamMatrix


class ParamVector:
    def __init__(self, start=None, stop=None, *args, **kwargs):
        self.start = start
        self.stop = stop
        self.params = { key: value for key, value in kwargs.items() }


Pv = ParamVector
