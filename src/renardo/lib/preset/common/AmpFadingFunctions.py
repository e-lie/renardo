from pprint import pprint

from renardo.runtime import player_method, linvar, inf, Clock, nextBar


@player_method
def curr_players(self):
    pprint(self.metro.playing)

@player_method
def ampfade(self, dur=4, famp=1, iamp=None, autostop=True):
    if iamp == None:
        iamp = float(self.amplify)
    self.amplify = linvar([iamp, famp], [dur, inf], start=Clock.mod(4))
    @nextBar(dur+1)
    def static_final_value():
        if famp == 0 and autostop:
            self.stop()
        else:
            self.amplify = famp
    return self

@player_method
def ampfadein(self, dur=4, famp=1, iamp=0, autostop=True):
    self.ampfade(dur=dur, famp=famp, iamp=iamp, autostop=autostop)
    return self

@player_method
def ampfadeout(self, dur=4, famp=0, iamp=1, autostop=True):
    self.ampfade(dur=dur, famp=famp, iamp=iamp, autostop=autostop)
    return self

@player_method
def sampfade(self, dur=16, iamp=None, famp=0, autostop=True):
    for player in list(self.metro.playing):
        if player is not self and not player.always_on:
            player.sampfade(dur, iamp, famp, autostop)
    return self

@player_method
def sampfadeout(self, dur=16, iamp=None, famp=0):
    self.sampfade(dur, iamp, famp)
    return self

@player_method
def sampfadein(self, dur=16, famp=1, iamp=None):
    self.sampfade(dur, iamp, famp)
    return self
