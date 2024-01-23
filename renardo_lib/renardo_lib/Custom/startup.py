### LOAD CUSTOM FX & SYNTHDEFS #####
try:
    from .Killa.synth_killa import *
    from .Killa.fx_killa import * 
except:
    print("Error importing custom SynthDefs or FX : ", sys.exc_info()[0])
