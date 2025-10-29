
from renardo_lib import Clock, linvar, sinvar, PWhite, PRand, inf, player_method, nextBar
from renardo_lib.Extensions.ReaperIntegrationLib.ReaTrack import ReaTrack

@player_method
def fadep(self, param_name, fvalue=1, dur=8, ivalue=None):
    """ general fade to value method working with any param """
    if ivalue == None:
        ivalue = float(self.__getattr__(param_name))
    self.__setattr__(param_name, linvar([ivalue, fvalue], [dur, inf], start=Clock.mod(4)))
    @nextBar(dur+1)
    def static_final_value():
        self.__setattr__(param_name, fvalue)
    return self

@player_method
def fade(self, dur=8, fvol=1, ivol=None, autostop=True):
    if "reatrack" in self.attr.keys() and isinstance(self.attr["reatrack"][0], ReaTrack):
        if ivol == None:
            ivol = float(self.vol)
        self.vol = linvar([ivol, fvol], [dur, inf], start=Clock.mod(4))
        @nextBar(dur+1)
        def static_final_value():
            if fvol == 0 and autostop:
                self.stop()
            else:
                self.vol = fvol
    else:
        self.ampfade(dur=dur, famp=fvol, iamp=ivol, autostop=autostop)
    return self

@player_method
def fadein(self, dur=8, fvol=1, ivol=0, autostop=True):
    self.fade(dur=dur, fvol=fvol, ivol=ivol, autostop=autostop)
    return self

@player_method
def fadeout(self, dur=8, fvol=0, ivol=None, autostop=True):
    self.fade(dur=dur, fvol=fvol, ivol=ivol, autostop=autostop)
    return self

@player_method
def fadeoutin(self, dur=32, outdur=16, mvol=0, fvol=1, ivol=None):
    self.fade(dur=dur/2, fvol=mvol, ivol=ivol, autostop=False)
    @nextBar(dur/2+1)
    def refadein():
        self.fade(dur=dur/2, ivol=None, fvol=fvol)
    return self

@player_method
def fadeinout(self, dur=32, outdur=16, mvol=1, fvol=0, ivol=None):
    self.fade(dur=dur/2, fvol=mvol, ivol=ivol, autostop=False)
    @nextBar(dur/2+1)
    def refadein():
        self.fade(dur=dur/2, ivol=None, fvol=fvol)
    return self


@player_method
def faderand(self, length=8):
    if "reatrack" in self.attr.keys() and isinstance(self.attr["reatrack"][0], ReaTrack):
        self.vol = sinvar([0] | PWhite(.2,1.2)[:length-1], [8] | PRand(1,4)[:length-1]*4, start=Clock.mod(4))
    else:
        self.amplify = sinvar([0] | PWhite(.2,1.2)[:length-1], [8] | PRand(1,4)[:length-1]*4, start=Clock.mod(4))
    return self
    
@player_method
def sfade(self, dur=16, fvol=0, ivol=None, autostop=True):
    for player in list(self.metro.playing):
        if player is not self:
            player.fade(dur=dur, ivol=ivol, fvol=fvol, autostop=autostop)
    return self

@player_method
def sfadeout(self, dur=16, fvol=0, ivol=None, autostop=True):
    self.sfade(dur=dur, fvol=fvol, ivol=ivol, autostop=autostop)
    return self

@player_method
def sfadein(self, dur=16, fvol=1, ivol=None, autostop=True):
    sfade(dur,fvol, ivol, autostop)
    return self


# Stereo fade methods (aliases for fadep with stereo parameters)

@player_method
def fadeo(self, dur=8, fvol=0.5, ivol=None):
    """Fade the 'stereo' parameter (0-0.5 range)"""
    return self.fadep("stereo", fvalue=fvol, dur=dur, ivalue=ivol)

@player_method
def fadeoo(self, dur=8, fvol=0.5, ivol=None):
    """Fade the 'stereoo' parameter (0-0.5 range)"""
    return self.fadep("stereoo", fvalue=fvol, dur=dur, ivalue=ivol)

@player_method
def fadeooo(self, dur=8, fvol=0.5, ivol=None):
    """Fade the 'stereooo' parameter (0-0.5 range)"""
    return self.fadep("stereooo", fvalue=fvol, dur=dur, ivalue=ivol)

@player_method
def fadeoooo(self, dur=8, fvol=0.5, ivol=None):
    """Fade the 'stereoooo' parameter (0-0.5 range)"""
    return self.fadep("stereoooo", fvalue=fvol, dur=dur, ivalue=ivol)


# Stereo fade-in methods (start from 0)

@player_method
def fadeino(self, dur=8, fvol=0.5):
    """Fade in the 'stereo' parameter from 0 to fvol (0-0.5 range)"""
    return self.fadep("stereo", fvalue=fvol, dur=dur, ivalue=0)

@player_method
def fadeinoo(self, dur=8, fvol=0.5):
    """Fade in the 'stereoo' parameter from 0 to fvol (0-0.5 range)"""
    return self.fadep("stereoo", fvalue=fvol, dur=dur, ivalue=0)

@player_method
def fadeinooo(self, dur=8, fvol=0.5):
    """Fade in the 'stereooo' parameter from 0 to fvol (0-0.5 range)"""
    return self.fadep("stereooo", fvalue=fvol, dur=dur, ivalue=0)

@player_method
def fadeinoooo(self, dur=8, fvol=0.5):
    """Fade in the 'stereoooo' parameter from 0 to fvol (0-0.5 range)"""
    return self.fadep("stereoooo", fvalue=fvol, dur=dur, ivalue=0)


# Stereo fade-out methods (to 0)

@player_method
def fadeouto(self, dur=8):
    """Fade out the 'stereo' parameter to 0"""
    return self.fadep("stereo", fvalue=0, dur=dur, ivalue=None)

@player_method
def fadeoutoo(self, dur=8):
    """Fade out the 'stereoo' parameter to 0"""
    return self.fadep("stereoo", fvalue=0, dur=dur, ivalue=None)

@player_method
def fadeoutooo(self, dur=8):
    """Fade out the 'stereooo' parameter to 0"""
    return self.fadep("stereooo", fvalue=0, dur=dur, ivalue=None)

@player_method
def fadeoutoooo(self, dur=8):
    """Fade out the 'stereoooo' parameter to 0"""
    return self.fadep("stereoooo", fvalue=0, dur=dur, ivalue=None)


# Cross fade methods (for cross, crosss, tutti parameters)

@player_method
def fadess(self, dur=8, fvol=0.5, ivol=None):
    """Fade the 'cross' parameter"""
    return self.fadep("cross", fvalue=fvol, dur=dur, ivalue=ivol)

@player_method
def fadesss(self, dur=8, fvol=0.5, ivol=None):
    """Fade the 'crosss' parameter"""
    return self.fadep("crosss", fvalue=fvol, dur=dur, ivalue=ivol)

@player_method
def fadet(self, dur=8, fvol=0.5, ivol=None):
    """Fade the 'tutti' parameter"""
    return self.fadep("tutti", fvalue=fvol, dur=dur, ivalue=ivol)


# Cross fade-in methods (start from 0)

@player_method
def fadeinss(self, dur=8, fvol=0.5):
    """Fade in the 'cross' parameter from 0 to fvol"""
    return self.fadep("cross", fvalue=fvol, dur=dur, ivalue=0)

@player_method
def fadeinsss(self, dur=8, fvol=0.5):
    """Fade in the 'crosss' parameter from 0 to fvol"""
    return self.fadep("crosss", fvalue=fvol, dur=dur, ivalue=0)

@player_method
def fadeint(self, dur=8, fvol=0.5):
    """Fade in the 'tutti' parameter from 0 to fvol"""
    return self.fadep("tutti", fvalue=fvol, dur=dur, ivalue=0)


# Cross fade-out methods (to 0)

@player_method
def fadeoutss(self, dur=8):
    """Fade out the 'cross' parameter to 0"""
    return self.fadep("cross", fvalue=0, dur=dur, ivalue=None)

@player_method
def fadeoutsss(self, dur=8):
    """Fade out the 'crosss' parameter to 0"""
    return self.fadep("crosss", fvalue=0, dur=dur, ivalue=None)

@player_method
def fadeoutt(self, dur=8):
    """Fade out the 'tutti' parameter to 0"""
    return self.fadep("tutti", fvalue=0, dur=dur, ivalue=None)


# Fade out all stereo and cross parameters

@player_method
def fadeoutall(self, dur=8):
    """Fade out all stereo, cross, and tutti parameters to 0"""
    # Fade out all stereo parameters
    self.fadep("stereo", fvalue=0, dur=dur, ivalue=None)
    self.fadep("stereoo", fvalue=0, dur=dur, ivalue=None)
    self.fadep("stereooo", fvalue=0, dur=dur, ivalue=None)
    self.fadep("stereoooo", fvalue=0, dur=dur, ivalue=None)
    # Fade out all cross/tutti parameters
    self.fadep("cross", fvalue=0, dur=dur, ivalue=None)
    self.fadep("crosss", fvalue=0, dur=dur, ivalue=None)
    self.fadep("tutti", fvalue=0, dur=dur, ivalue=None)
    return self


