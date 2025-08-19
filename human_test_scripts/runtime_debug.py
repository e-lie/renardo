
import time


from renardo.runtime import *

reaproject.clear_reaper()

bass303 = ReaperInstrument(
    shortname='bass303',
    fullname='Bass 303',
    description='Acid bass with TB-303 resonance',
    fxchain_path='bass303.RfxChain',
    arguments={},
    bank='0_renardo_core',
    category='bass'
)

b4 >> bass303([0,2,0,4])

reverb = ReaperEffect(
      shortname='delayverb',
      fxchain_path='delayverb.RfxChain',
      fullname='delayverb',
      description='Delay and reverb from Surge',
      bank='0_renardo_core',
      category='reverb'
)


b1 >> bass303([0,4,5,3], cool=-6, volin=0)



time.sleep(2)
b1 >> bass303([0,4,5,3], cool=0)


reaproject.create_bus_track("cool2")


equals = ReaperInstrument(
    shortname='equals',
    fullname='Equald Lead',
    description='',
    fxchain_path='equals.RfxChain',
    arguments={},
    bank='0_renardo_core',
    category='lead'
)





equals.add_send("cool")
bass303.add_send("cool2")



b1 >> bass303([0,4,5,3])
b2 >> equals([0,4,5,3], dur=.5)



reaproject.tracks[0].add_send_to_track(reaproject.tracks[2])


b1 >> bass303([0,4,5,3], cutoff=linvar([0,1]), delay_mix=linvar([1,0]), rea_eq_freq_low_shelf=linvar([0,1]))




Clock.clear()
b1 >> bass303([0,4,5,3], cutoff=var([0,1]))

b2 >> blip()
#m1 >> MidiOut([0,2,0,4])


time.sleep(10)

reaproject: ReaProject

reaproject.create_16_midi_tracks()