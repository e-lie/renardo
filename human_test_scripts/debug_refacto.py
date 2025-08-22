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

reverb = ReaperEffect(
      shortname='delayverb',
      fxchain_path='delayverb.RfxChain',
      fullname='delayverb',
      description='Delay and reverb from Surge',
      bank='0_renardo_core',
      category='reverb'
)

b4 >> bass303([0,2,0,4], cutoff=linvar([0,1]))


import time
time.sleep(15)