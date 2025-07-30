
import time
from renardo.runtime import *

#b1 >> blip(P[0,2,0,5]+P*(0,2), dur=.5, amp=[.3,.7,1], sus=1)+var([0,1,2,4,5],[1,2])
#b2 >> blip(P[0,2,0,5], dur=.5, amp=[.3,.7,1], sus=1, oct=3)+var([0,1,2,4,5],[1,2])

reaproject: ReaProject

#reaproject.create_16_midi_tracks()

bass303 = ReaperInstrument(
    shortname='bass303',
    fullname='Bass 303',
    description='Acid bass with TB-303 resonance',
    fxchain_path='bass303.RfxChain',
    arguments={},
    bank='0_renardo_core',
    category='bass'
)


print(bass303)

time.sleep(10)