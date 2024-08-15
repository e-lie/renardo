from renardo_lib.SCLang.SCLangExperimentalBindings import *
from renardo_lib.SCLang.SynthDef import DefaultSynthDef
from renardo_lib.SCLang.SampleSynthDefs import SampleSynthDef, LoopSynthDef, StretchSynthDef, GranularSynthDef
from renardo_lib.SCLang.SCLangExperimentalBindings import Env

# Sample Player

with SampleSynthDef("play1") as play:
    play.osc = PlayBuf.ar(1, play.buf, BufRateScale.ir(
        play.buf) * play.rate, startPos=BufSampleRate.kr(play.buf) * play.pos)
    play.osc = play.osc * play.amp

with SampleSynthDef("play2") as play:
    play.osc = PlayBuf.ar(2, play.buf, BufRateScale.ir(
        play.buf) * play.rate, startPos=BufSampleRate.kr(play.buf) * play.pos)
    play.osc = play.osc * play.amp


loop = LoopSynthDef()
stretch = StretchSynthDef()
granular = GranularSynthDef()

# Synth Players

with DefaultSynthDef("audioin") as audioin:
    audioin.defaults.update(channel=1)
    audioin.osc = AudioIn.ar(audioin.channel)
    audioin.env = Env.mask()