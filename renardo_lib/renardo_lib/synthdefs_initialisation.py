from renardo_lib.SCLang.SCLang import *
from renardo_lib.SCLang.SynthDef import SynthDef, SampleSynthDef, FileSynthDef
from renardo_lib.Settings import SC3_PLUGINS

from renardo_lib.SCLang import Env

# Sample Player

with SampleSynthDef("play1") as play:
    play.osc = PlayBuf.ar(1, play.buf, BufRateScale.ir(
        play.buf) * play.rate, startPos=BufSampleRate.kr(play.buf) * play.pos)
    play.osc = play.osc * play.amp

with SampleSynthDef("play2") as play:
    play.osc = PlayBuf.ar(2, play.buf, BufRateScale.ir(
        play.buf) * play.rate, startPos=BufSampleRate.kr(play.buf) * play.pos)
    play.osc = play.osc * play.amp

# Synth Players

with SynthDef("audioin") as audioin:
    audioin.defaults.update(channel=1)
    audioin.osc = AudioIn.ar(audioin.channel)
    audioin.env = Env.mask()

# with SynthDef("sinepad") as sinepad:
#     sinepad.amp = sinepad.amp * 1.5
#     sinepad.freq = sinepad.freq + [0,2]
#     sinepad.osc = SinOsc.ar(sinepad.freq, mul=sinepad.amp)
#     sinepad.osc = HPF.ar(sinepad.osc, 1000);
#     sinepad.env = Env.perc()
    # sinepad.env = Env.perc()

with SynthDef("noise") as noise:
    noise.freq = noise.freq * 2
    noise.osc = LFNoise0.ar(noise.freq, noise.amp)
    noise.env = Env.perc()

with SynthDef("dab") as synth:
    a = HPF.ar(Saw.ar(synth.freq / 4, mul=synth.amp / 2), 2000)
    b = VarSaw.ar(synth.freq / 4, mul=synth.amp,
                  width=Env.perc(synth.sus / 20, synth.sus / 4, 0.5, -5, doneAction=0))
    synth.osc = a + b
    synth.env = Env.env(sus=[Env.sus * 0.25, Env.sus * 1], curve="'lin'")
dab = synth
del a
del b

with SynthDef("varsaw") as synth:
    synth.freq = synth.freq * [1, 1.005]
    synth.osc = VarSaw.ar(synth.freq, mul=synth.amp / 4, width=synth.rate)
    synth.env = Env.env()
varsaw = synth

with SynthDef("lazer") as synth:
    synth.freq = synth.freq * [1, 1.005]
    synth.amp = synth.amp * 0.1
    synth.osc = VarSaw.ar(synth.freq,  width=(synth.rate-1)/4) + LFSaw.ar(LFNoise0.ar(
        synth.rate * 20, add=synth.freq * Pulse.ar((synth.rate-2) + 0.1, add=1), mul=0.5))
    synth.env = Env.perc(0.1)
lazer = synth

with SynthDef("growl") as growl:
    growl.sus = growl.sus * 1.5
    growl.osc = SinOsc.ar(growl.freq + SinOsc.kr(0.5, add=1, mul=2),
                          mul=growl.amp) * Saw.ar((growl.sus / 1.5) * 32)
    growl.env = Env.env()

with SynthDef("dirt") as dirt:
    dirt.freq = dirt.freq / 4
    dirt.amp = dirt.amp / 2
    dirt.osc = LFSaw.ar(dirt.freq, mul=dirt.amp) + VarSaw.ar(dirt.freq + 1,
                                                             width=0.85, mul=dirt.amp) + SinOscFB.ar(dirt.freq - 1, mul=dirt.amp/2)
    dirt.env = Env.perc()

with SynthDef("crunch") as crunch:
    crunch.amp = crunch.amp * 0.5
    crunch.osc = LFNoise0.ar(Crackle.kr(
        1.95) * crunch.freq * 15, mul=crunch.amp)
    crunch.env = Env.perc(0.01, 0.1, crunch.amp / 4)

with SynthDef("rave") as rave:
    rave.osc = Gendy1.ar(rave.rate-1, mul=rave.amp/2,
                         minfreq=rave.freq, maxfreq=rave.freq*2)
    rave.env = Env.perc()

with SynthDef("scatter") as scatter:
    scatter.osc = (Saw.ar(scatter.freq, mul=scatter.amp / 8) + VarSaw.ar(
        scatter.freq + [2, 1],  mul=scatter.amp/8)) * LFNoise0.ar(scatter.rate)
    scatter.env = Env.linen(0.01, scatter.sus/2, scatter.sus/2)

with SynthDef("charm") as charm:
    charm.freq = charm.freq + [0, 2]
    charm.freq = charm.freq * [1, 2]
    charm.osc = SinOsc.ar(charm.freq, mul=charm.amp / 4) + \
        VarSaw.ar(charm.freq * 8, 10, mul=charm.amp/8)
    charm.osc = LPF.ar(charm.osc, SinOsc.ar(
        Line.ar(1, charm.rate*4, charm.sus/8), 0, charm.freq*2, charm.freq*2 + 10))
    charm.env = Env.perc()

with SynthDef("bell") as bell:
    bell.defaults.update(verb=0.5, room=0.5, rate=1)
    bell.amp = bell.amp * 4
    bell.osc = Klank.ar([[0.501, 1, 0.7,   2.002, 3, 9.6,   2.49, 11, 2.571,  3.05, 6.242, 12.49, 13, 16, 24],
                         [0.002, 0.1, 0.001, 0.008, 0.02, 0.004, 0.02, 0.04,
                             0.02, 0.005, 0.05, 0.05, 0.02, 0.03, 0.04],
                         stutter([1.2, 0.9, 0.25, 0.14, 0.07], 3)], Impulse.ar(0.01), bell.freq, 0, 4 * bell.rate) * bell.amp

with SynthDef("gong") as gong:
    gong.amp = gong.amp * 2.5
    gong.freq = gong.freq * 2
    gong.osc = Klank.ar([[0.501, 1, 0.8, 2.002, 3, 9.6, 2.49, 11, 2.571, 3.05, 6.242, 12.49, 13, 16, 24],
                         [0.002, 0.02, 0.001, 0.008, 0.02, 0.004, 0.02, 0.04,
                          0.02, 0.005, 0.05, 0.05, 0.02, 0.03, 0.04],
                        [1.2, 1.2, 1.2, 0.9, 0.9, 0.9, 0.25, 0.25, 0.25, 0.14, 0.14, 0.14, 0.07, 0.07, 0.07]],
                        SinOscFB.ar(20, 0, 10), gong.freq, gong.freq * gong.rate, 4) * gong.amp
    gong.osc = HPF.ar(gong.osc, 440)


with SynthDef("soprano") as soprano:
    soprano.sus = soprano.sus * 1.75
    soprano.amp = soprano.amp / 2
    soprano.freq = Vibrato.kr(soprano.freq, soprano.rate+4)
    soprano.osc = SinOsc.ar(soprano.freq * 3, mul=soprano.amp) + \
        SinOscFB.ar(soprano.freq * 3, mul=soprano.amp / 2)
    soprano.env = Env.env()

with SynthDef("dub") as dub:
    dub.freq = dub.freq / 4
    dub.amp = dub.amp * 2
    dub.osc = LFTri.ar(dub.freq, mul=dub.amp) + \
        SinOscFB.ar(dub.freq, mul=dub.amp)
    dub.env = Env.sine(dur=dub.sus)

with SynthDef("scratch") as scratch:
    scratch.defaults.update(depth=0.5, rate=0.04)
    scratch.amp = scratch.amp / 4
    scratch.freq = scratch.freq * Crackle.ar(1.5)
    scratch.osc = SinOsc.ar(Vibrato.kr(
        scratch.freq, 2, 3, rateVariation=scratch.rate, depthVariation=scratch.depth), mul=scratch.amp)
    scratch.env = Env.env()

with SynthDef("klank") as klank:
    klank.sus = klank.sus * 1.5
    klank.osc = Klank.ar([[1, 2, 3, 4], [1, 1, 1, 1], [
                         2, 2, 2, 2]], ClipNoise.ar(0.0005).dup, klank.freq)
    if SC3_PLUGINS:
        klank.osc = Decimator.ar(klank.osc, bits=klank.rate - 1)
    klank.env = Env.env(klank.sus*2)

with SynthDef("feel") as feel:
    feel.sus = feel.sus * 1.5
    feel.amp = feel.amp / 3
    feel.freq = feel.freq * [1, 1.005]
    feel.osc = Klank.ar([[1, 2, 3, 3 + ((feel.rate-1)/10)], [1, 1, 1, 1],
                        [2, 2, 2, 2]], Impulse.ar(0.0005) * Saw.ar(feel.freq, add=1), feel.freq)
    feel.env = Env.env(feel.sus*2)

with SynthDef("glass") as glass:
    glass.sus = glass.sus * 1.5
    glass.amp = glass.amp * 1.5
    glass.freq = glass.freq * [1, (1 + (0.005 * glass.rate))]
    glass.osc = Klank.ar([[2, 4, 9, 16], [1, 1, 1, 1], [2, 2, 2, 2]], PinkNoise.ar(
        0.0005).dup * SinOsc.ar(glass.freq / 4, add=1, mul=0.5), glass.freq)
    glass.env = Env.env(glass.sus*2)

with SynthDef("soft") as soft:
    soft.freq = soft.freq/2
    soft.amp = soft.amp / (200 * (1 + soft.rate))
    soft.osc = Klank.ar([[7, 5, 3, 1], [8, 4, 2, 1], [2, 4, 8, 16]],
                        LFNoise0.ar(soft.rate/soft.sus), soft.freq)
    soft.env = Env.env(soft.sus)


with SynthDef("quin") as synth:
    synth.amp = synth.amp
    synth.freq = synth.freq * [1, 1.01]
    synth.osc = Klank.ar([[1, 2, 4, 2], [100, 50, 0, 10], [1, 5, 0, 1]], Impulse.ar(
        synth.freq).dup, synth.freq) / 5000
    synth.osc = synth.osc * LFSaw.ar(synth.freq * (1 + synth.rate))
    synth.env = Env.perc(atk=0.01, sus=synth.sus, curve=1)
quin = synth

with SynthDef("pluck") as pluck:
    freq = instance('freq')
    pluck.amp = pluck.amp + 0.00001
    pluck.freq = pluck.freq + [0, LFNoise2.ar(50).range(-2, 2)]
    pluck.osc = SinOsc.ar(freq * 1.002, phase=VarSaw.ar(freq, width=Line.ar(1, 0.2, 2))) * \
        0.3 + SinOsc.ar(freq, phase=VarSaw.ar(freq,
                        width=Line.ar(1, 0.2, 2))) * 0.3
    pluck.osc = pluck.osc * \
        XLine.kr(pluck.amp, pluck.amp/10000, pluck.sus * 4, doneAction=2) * 0.3

with SynthDef("spark") as synth:
    freq = instance('freq')
    synth.amp = synth.amp + 0.00001
    synth.freq = synth.freq + [0, LFNoise2.ar(50).range(-2, 2)]
    synth.osc = LFSaw.ar(freq * 1.002, iphase=Saw.ar(0.1)) * \
        0.3 + LFSaw.ar(freq, iphase=Saw.ar(0.1)) * 0.3
    synth.osc = (synth.osc * Line.ar(synth.amp, synth.amp/10000,
                 synth.sus * 1.5) * 0.3) * Line.ar(0.01, 1, synth.sus * 0.033)
spark = synth

with SynthDef("blip") as synth:
    freq = instance('freq')
    synth.amp = synth.amp + 0.00001
    synth.freq = freq + [0, LFNoise2.ar(50).range(-2, 2)]
    synth.freq = synth.freq * 2
    synth.osc = (LFCub.ar(freq * 1.002, iphase=1.5) + LFTri.ar(freq,
                 iphase=Line.ar(2, 0, 0, 2)) * 0.3) * Blip.ar(freq / 2, synth.rate)
    synth.osc = synth.osc * \
        XLine.ar(synth.amp, synth.amp/10000, synth.sus * 2) * 0.3
blip = synth
del freq

with SynthDef("ripple") as ripple:
    ripple.amp = ripple.amp / 6
    ripple.osc = Pulse.ar(ripple.freq/4, 0.2, 0.25) + \
        Pulse.ar(ripple.freq+1, 0.5, 0.5)
    ripple.osc = ripple.osc * SinOsc.ar(ripple.rate/ripple.sus, 0, 0.5, 1)
    ripple.env = Env.env(sus=[0.55 * ripple.sus, 0.55*ripple.sus])

with SynthDef("creep") as creep:
    creep.amp = creep.amp / 4
    creep.osc = PMOsc.ar(creep.freq, creep.freq * 2, 10)
    creep.env = Env.reverse()

# No context manager SynthDef creation

orient = SynthDef("orient")
orient.defaults.update(room=10, verb=0.7)
orient.osc = LFPulse.ar(orient.freq, 0.5, 0.25, 1/4) + \
                        LFPulse.ar(orient.freq, 1, 0.1, 1/4)
orient.env = Env.perc()
orient.add()

zap = SynthDef("zap")
zap.defaults.update(room=0, verb=0)
zap.amp = zap.amp / 10
zap.osc = Saw.ar(zap.freq * [1, 1.01] + LFNoise2.ar(50).range(-2, 2)) + \
                 VarSaw.ar(zap.freq + LFNoise2.ar(50).range(-2, 2), 1)
zap.env = Env.perc(atk=0.025, curve=-10)
zap.add()

marimba = SynthDef("marimba")
marimba.osc = Klank.ar([[1/2, 1, 4, 9], [1/2, 1, 1, 1], [1, 1, 1, 1]],
                       PinkNoise.ar([0.007, 0.007]), marimba.freq, [0, 2])
marimba.sus = 1
marimba.env = Env.perc(atk=0.001, curve=-6)
marimba.add()

fuzz = SynthDef("fuzz")
fuzz.freq = fuzz.freq / 2
fuzz.amp = fuzz.amp / 6
fuzz.osc = LFSaw.ar(LFSaw.kr(fuzz.freq, 0, fuzz.freq, fuzz.freq * 2))
fuzz.env = Env.ramp(amp=[1, 1, 0.01], sus=[fuzz.sus * 0.8, 0.01])
fuzz.add()

bug = SynthDef("bug")
bug.defaults.update(rate=1)
bug.amp = bug.amp / 5
bug.freq = bug.freq * [1, 1.0001]
bug.osc = Pulse.ar(
    bug.freq, width=[0.09, 0.16, 0.25]) * SinOsc.ar(bug.rate * 4)
bug.env = Env.perc(bug.sus * 1.5)
bug.add()

pulse = SynthDef("pulse")
pulse.amp = pulse.amp / 8
pulse.osc = Pulse.ar(pulse.freq)
pulse.osc = pulse.osc * pulse.amp
pulse.env = Env.mask()
pulse.add()

saw = SynthDef("saw")
saw.amp = saw.amp / 8
saw.osc = Saw.ar(saw.freq)
saw.osc = saw.osc * saw.amp
saw.env = Env.mask()
saw.add()

snick = SynthDef("snick")
snick.osc = LFPar.ar(snick.freq, mul=1) * Blip.ar(((snick.rate+1) * 4))
snick.env = Env.perc()
snick.add()

twang = SynthDef("twang")
twang.freq = twang.freq / 8
twang.freq = twang.freq + [0, 2]
twang.osc = LPF.ar(Impulse.ar(twang.freq, 0.1), 4000)
twang.osc = Env.perc() * CombL.ar(twang.osc, delaytime=twang.rate
                                  / (twang.freq * 8), maxdelaytime=0.25)
twang.add()

karp = SynthDef("karp")
karp.amp = karp.amp * 0.75
karp.osc = LFNoise0.ar(400 + (400 * karp.rate), karp.amp)
karp.osc = karp.osc * XLine.ar(1, 0.000001, karp.sus * 0.1)
karp.freq = (265 / (karp.freq * 0.666)) * 0.005
karp.osc = CombL.ar(karp.osc, delaytime=karp.freq, maxdelaytime=2)
karp.env = Env.ramp()
karp.add()

arpy = SynthDef("arpy")
arpy.freq = arpy.freq / 2
arpy.amp = arpy.amp * 2
arpy.freq = arpy.freq + [0, 0.5]
arpy.osc = LPF.ar(Impulse.ar(arpy.freq), 3000)
arpy.env = Env.perc(sus=arpy.sus * 0.25)
arpy.add()

nylon = SynthDef("nylon")
nylon.osc = LFPulse.ar(nylon.freq, 0.5, 0.33 * nylon.rate,
                       0.25) + LFPar.ar(nylon.freq + 0.5, 1, 0.1, 0.25)
nylon.env = Env.perc(curve=-4, atk=0.000125, sus=Env.sus * 3)
nylon.add()

donk = SynthDef("donk")
donk.freq = (donk.freq / 2) + [0, 2]
donk.amp = donk.amp / 1.25
donk.osc = Ringz.ar(Impulse.ar(0, phase=donk.rate)
                    / (donk.rate+1), donk.freq, donk.sus, donk.amp)
donk.add()

squish = SynthDef("squish")
squish.freq = squish.freq / 4
squish.osc = Ringz.ar(Pulse.ar(4 * squish.rate),
                      squish.freq, squish.sus, squish.amp)
squish.osc = squish.osc * XLine.ar(1/2, 0.000001, squish.sus, doneAction=2)
squish.osc = squish.osc.cos
squish.amp = squish.amp * 4
squish.add()

swell = SynthDef("swell")
swell.defaults.update(rate=1)
swell.amp = swell.amp / 4
swell.freq = swell.freq + [0, 1]
swell.freq = swell.freq * [1, 0.5]
swell.osc = VarSaw.ar(swell.freq, width=SinOsc.ar(
    swell.rate / (2 * swell.sus / 1.25), add=0.5, mul=[0.5, 0.5]), mul=[1, 0.5])
swell.env = Env.perc()
swell.add()

# Credit to Thor Magnusson for brass

razz = SynthDef("razz")
razz.defaults.update(rate=0.3)
razz.freq = razz.freq + [0, 1]
razz.rate = Lag.ar(K2A.ar(razz.freq), razz.rate)
razz.osc = Saw.ar(razz.rate * [1, 1/2], [1, 1/3]) + \
                  Saw.ar(razz.rate+LFNoise2.ar(4).range(0.5, 2.5), 1)
razz.osc = BPF.ar(razz.osc, razz.freq * 2.5, 0.3)
razz.osc = RLPF.ar(razz.osc, 1300, 0.78)
razz.env = Env.perc(atk=0.125)
razz.add()

sitar = SynthDef("sitar")
sitar.amp = sitar.amp * 0.75
sitar.sus = sitar.sus * 4
sitar.osc = LFNoise0.ar([8400, 8500], sitar.amp)
sitar.osc = sitar.osc * XLine.ar(1, 0.000001, sitar.sus * 0.1)
sitar.freq = (265 / (sitar.freq * [0.666, 0.669])) * 0.005
sitar.osc = CombL.ar(sitar.osc, delaytime=sitar.freq, maxdelaytime=2)
sitar.env = Env.ramp()
sitar.add()

with SynthDef("star") as synth:
    freq = instance('freq')
    synth.amp = (synth.amp * 2) + 0.00001
    synth.freq = synth.freq / 2
    synth.osc = LFSaw.ar(freq * 1.002, iphase=VarSaw.kr(freq, width=Line.kr(1, 0.2, synth.sus))) * 0.3 + LFSaw.ar(
        freq + LFNoise2.ar(50).range(-2, 2) + 2, iphase=VarSaw.kr(freq + 2, width=Line.kr(1, 0.2, synth.sus))) * 0.3
    synth.osc = synth.osc * XLine.ar(synth.amp, synth.amp/10000,
                                     synth.sus * 3, doneAction=2) * Line.ar(0.01, 0.5, 0.07)
star = synth

with SynthDef("jbass") as jbass:
    jbass.freq = jbass.freq / 4
    jbass.amp = jbass.amp * 0.8
    jbass.osc = LFTri.ar(jbass.freq, mul=jbass.amp)
    jbass.adsr(atk=0.01, decay=0.01, rel=0.01)

# Possible future syntax?
# -----------------------
# @SynthDef
# def jbass(amp = 0.8):
#     freq = freq / 4
#     return


if SC3_PLUGINS:

    piano = SynthDef("piano")
    piano.amp = piano.amp * 0.7
    piano.osc = MdaPiano.ar(
        piano.freq[0], vel=40 + (piano.amp * 60), decay=piano.sus / 4)
    piano.env = Env.ramp()
    piano.add()

# SynthDefs read from file
bass = FileSynthDef('bass')
bass.add()

dirt = FileSynthDef('dirt')
dirt.add()

sawbass = FileSynthDef('sawbass')
sawbass.add()

prophet = FileSynthDef('prophet')
prophet.add()

pads = FileSynthDef('pads')
pads.add()

pasha = FileSynthDef('pasha')
pasha.add()

ambi = FileSynthDef("ambi")
ambi.add()

space = FileSynthDef("space")
space.add()

keys = FileSynthDef("keys")
keys.add()

bass = FileSynthDef("bass")
bass.add()

dbass = FileSynthDef("dbass")
dbass.add()

sinepad = FileSynthDef("sinepad")
sinepad.add()

video = FileSynthDef("video")
video.add()

viola = FileSynthDef("viola")
viola.add()

hydra = FileSynthDef("hydra")
hydra.add()

abass = FileSynthDef("abass")
abass.add()

acidbass = FileSynthDef("acidbass")
acidbass.add()

alva = FileSynthDef("alva")
alva.add()

angel = FileSynthDef("angel")
angel.add()

angst = FileSynthDef("angst")
angst.add()

bassguitar = FileSynthDef("bassguitar")
bassguitar.add()

bbass = FileSynthDef("bbass")
bbass.add()

bchaos = FileSynthDef("bchaos")
bchaos.add()

bellmod = FileSynthDef("bellmod")
bellmod.add()

benoit = FileSynthDef("benoit")
benoit.add()

birdy = FileSynthDef("birdy")
birdy.add()

blips = FileSynthDef("blips")
blips.add()

bnoise = FileSynthDef("bnoise")
bnoise.add()

borgan = FileSynthDef("borgan")
borgan.add()

bounce = FileSynthDef("bounce")
bounce.add()

bphase = FileSynthDef("bphase")
bphase.add()

brass = FileSynthDef("brass")
brass.add()

brown = FileSynthDef("brown")
brown.add()

chimebell = FileSynthDef("chimebell")
chimebell.add()

chipsy = FileSynthDef("chipsy")
chipsy.add()

click = FileSynthDef("click")
click.add()

clip = FileSynthDef("clip")
clip.add()

cluster = FileSynthDef("cluster")
cluster.add()

combs = FileSynthDef("combs")
combs.add()

cs80lead = FileSynthDef("cs80lead")
cs80lead.add()

dafbass = FileSynthDef("dafbass")
dafbass.add()

dblbass = FileSynthDef("dblbass")
dblbass.add()

donkysub = FileSynthDef("donkysub")
donkysub.add()

donorgan = FileSynthDef("donorgan")
donorgan.add()

dopple = FileSynthDef("dopple")
dopple.add()

drone = FileSynthDef("drone")
drone.add()

dustv = FileSynthDef("dustv")
dustv.add()

ebass = FileSynthDef("ebass")
ebass.add()

ecello = FileSynthDef("ecello")
ecello.add()

eeri = FileSynthDef("eeri")
eeri.add()

eoboe = FileSynthDef("eoboe")
eoboe.add()

epiano = FileSynthDef("epiano")
epiano.add()

faim = FileSynthDef("faim")
faim.add()

faim2 = FileSynthDef("faim2")
faim2.add()

fbass = FileSynthDef("fbass")
fbass.add()

filthysaw = FileSynthDef("filthysaw")
filthysaw.add()

flute = FileSynthDef("flute")
flute.add()

fm = FileSynthDef("fm")
fm.add()

fmbass = FileSynthDef("fmbass")
fmbass.add()

fmrhodes = FileSynthDef("fmrhodes")
fmrhodes.add()

garfield = FileSynthDef("garfield")
garfield.add()

# gaze = FileSynthDef("gaze")
# gaze.add()

glitchbass = FileSynthDef("glitchbass")
glitchbass.add()

glitcher = FileSynthDef("glitcher")
glitcher.add()

grat = FileSynthDef("grat")
grat.add()

gray = FileSynthDef("gray")
gray.add()

gsynth = FileSynthDef("gsynth")
gsynth.add()

harp = FileSynthDef("harp")
harp.add()

hnoise = FileSynthDef("hnoise")
hnoise.add()

hoover = FileSynthDef("hoover")
hoover.add()

kalimba = FileSynthDef("kalimba")
kalimba.add()

ladder = FileSynthDef("ladder")
ladder.add()

lapin = FileSynthDef("lapin")
lapin.add()

laserbeam = FileSynthDef("laserbeam")
laserbeam.add()

latoo = FileSynthDef("latoo")
latoo.add()

lazer = FileSynthDef("lazer")
lazer.add()

lfnoise = FileSynthDef("lfnoise")
lfnoise.add()

linesaw = FileSynthDef("linesaw")
linesaw.add()

longsaw = FileSynthDef("longsaw")
longsaw.add()

mhpad = FileSynthDef("mhpad")
mhpad.add()

mhping = FileSynthDef("mhping")
mhping.add()

moogbass = FileSynthDef("moogbass")
moogbass.add()

moogpluck = FileSynthDef("moogpluck")
moogpluck.add()

moogpluck2 = FileSynthDef("moogpluck2")
moogpluck2.add()

mpluck = FileSynthDef("mpluck")
mpluck.add()

noisynth = FileSynthDef("noisynth")
noisynth.add()

noquarter = FileSynthDef("noquarter")
noquarter.add()

organ = FileSynthDef("organ")
organ.add()

organ2 = FileSynthDef("organ2")
organ2.add()

pbass = FileSynthDef("pbass")
pbass.add()

phazer = FileSynthDef("phazer")
phazer.add()

pianovel = FileSynthDef("pianovel")
pianovel.add()

pink = FileSynthDef("pink")
pink.add()

pmcrotal = FileSynthDef("pmcrotal")
pmcrotal.add()

ppad = FileSynthDef("ppad")
ppad.add()

prayerbell = FileSynthDef("prayerbell")
prayerbell.add()

prof = FileSynthDef("prof")
prof.add()

radio = FileSynthDef("radio")
radio.add()

rhodes = FileSynthDef("rhodes")
rhodes.add()

rhpiano = FileSynthDef("rhpiano")
rhpiano.add()

risseto = FileSynthDef("risseto")
risseto.add()

rissetobell = FileSynthDef("rissetobell")
rissetobell.add()

rlead = FileSynthDef("rlead")
rlead.add()

rsaw = FileSynthDef("rsaw")
rsaw.add()

rsin = FileSynthDef("rsin")
rsin.add()

scatter = FileSynthDef("scatter")
scatter.add()

shore = FileSynthDef("shore")
shore.add()

sillyvoice = FileSynthDef("sillyvoice")
sillyvoice.add()

sine = FileSynthDef("sine")
sine.add()

siren = FileSynthDef("siren")
siren.add()

spacesaw = FileSynthDef("spacesaw")
spacesaw.add()

sos = FileSynthDef("sos")
sos.add()

sosbell = FileSynthDef("sosbell")
sosbell.add()

spick = FileSynthDef("spick")
spick.add()

sputter = FileSynthDef("sputter")
sputter.add()

square = FileSynthDef("square")
square.add()

ssaw = FileSynthDef("ssaw")
ssaw.add()

# stargazer = FileSynthDef("stargazer")
# stargazer.add()

steeldrum = FileSynthDef("steeldrum")
steeldrum.add()

strings = FileSynthDef("strings")
strings.add()

subbass = FileSynthDef("subbass")
subbass.add()

subbass2 = FileSynthDef("subbass2")
subbass2.add()

supersaw = FileSynthDef("supersaw")
supersaw.add()

tb303 = FileSynthDef("tb303")
tb303.add()

total = FileSynthDef("total")
total.add()

tremsynth = FileSynthDef("tremsynth")
tremsynth.add()

tribell = FileSynthDef("tribell")
tribell.add()

tritri = FileSynthDef("tritri")
tritri.add()

triwave = FileSynthDef("triwave")
triwave.add()

tubularbell = FileSynthDef("tubularbell")
tubularbell.add()

tworgan = FileSynthDef("tworgan")
tworgan.add()

tworgan2 = FileSynthDef("tworgan2")
tworgan2.add()

tworgan3 = FileSynthDef("tworgan3")
tworgan3.add()

tworgan4 = FileSynthDef("tworgan4")
tworgan4.add()

varicelle = FileSynthDef("varicelle")
varicelle.add()

vibass = FileSynthDef("vibass")
vibass.add()

vinsine = FileSynthDef("vinsine")
vinsine.add()

virus = FileSynthDef("virus")
virus.add()

waves = FileSynthDef("waves")
waves.add()

windmaker = FileSynthDef("windmaker")
windmaker.add()

wobble = FileSynthDef("wobble")
wobble.add()

wobblebass = FileSynthDef("wobblebass")
wobblebass.add()

wsaw = FileSynthDef("wsaw")
wsaw.add()

wsawbass = FileSynthDef("wsawbass")
wsawbass.add()

xylophone = FileSynthDef("xylophone")
xylophone.add()

# Get rid of the variable synth

del synth
