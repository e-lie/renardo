from enum import Enum


class ReaParamState(Enum):
    NORMAL = 0
    VAR1 = 1
    VAR2 = 2


class ReaParam(object):
    def __init__(self, name, value, index=None, reaper_name=None, state=ReaParamState.NORMAL):
        self.name = name
        self.index = index
        self.value = value
        self.reaper_name = reaper_name
        self.state: ReaParamState = state


class ReaSend(ReaParam):
    def __repr__(self):
        return "<ReaSend {}>".format(self.name)
