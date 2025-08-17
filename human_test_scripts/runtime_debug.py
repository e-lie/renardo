
import time


from renardo.runtime import *

bass303 = ReaperInstrument(
    shortname='bass303',
    fullname='Bass 303',
    description='Acid bass with TB-303 resonance',
    fxchain_path='bass303.RfxChain',
    arguments={},
    bank='0_renardo_core',
    category='bass'
)

b1 >> bass303([0,4,5,3], cutoff=var([0,1]), delay_mix=1)
Clock.clear()
b1 >> bass303([0,4,5,3], cutoff=var([0,1]))

b2 >> blip()
#m1 >> MidiOut([0,2,0,4])


time.sleep(10)

reaproject: ReaProject

#reaproject.create_16_midi_tracks()