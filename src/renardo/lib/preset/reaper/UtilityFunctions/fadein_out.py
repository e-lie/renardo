
from renardo.runtime import Clock, linvar, sinvar, PWhite, PRand, inf, player_method, nextBar
from renardo.reaper_backend.ReaperIntegrationLib.ReaTrack import ReaTrack

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


