from renardo.lib.runtime import Player

def switch(player_running, new_player, dur=8):
    player_running.fadeout(dur)
    new_player.fadein(dur)

class BiInstrument:
    """
    class to combine two synthproxy with a mix parameter handling mixing volume of the two
    
    bluck = BiInstrument(blip, pluck)
    bluck.start([0,2,4], mix=linvar([0,1],16))
    bluck.stop()
    """
    def __init__(self, instru1, instru2, mix=0, biamp=1):
        self.instru1 = instru1
        self.instru2 = instru2
        self.player1 = Player()
        self.player2 = Player()
        self.mix=mix
        self.biamp=biamp

    def start(self, *args, **kwargs):
        if "mix" in kwargs.keys():
            self.mix = kwargs["mix"]
        if "biamp" in kwargs.keys():
            self.biamp = kwargs["biamp"]
        self.player1 >> self.instru1(*args, **kwargs)
        self.player2 >> self.instru2(*args, **kwargs)
        self.player2.amplify = self.mix * self.biamp
        self.player1.amplify = (1 - self.mix) * self.biamp

    def stop(self):
        self.player1.stop()
        self.player2.stop()