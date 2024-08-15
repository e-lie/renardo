from renardo_lib.SynthDefManagement.SCLangExperimentalPythonBindings.core import format_args, cls

# UGens

SinOsc = cls("SinOsc")
SinOscFB = cls("SinOscFB")
Saw = cls("Saw")
LFSaw = cls("LFSaw")
VarSaw = cls("VarSaw")
LFTri = cls("LFTri")
LFPar = cls("LFPar")
PlayBuf = cls("PlayBuf")
LFNoise0 = cls("LFNoise0")
LFNoise1 = cls("LFNoise1")
LFNoise2 = cls("LFNoise2")
Gendy1 = cls("Gendy1")
Gendy2 = cls("Gendy2")
Gendy3 = cls("Gendy3")
Gendy4 = cls("Gendy4")
Gendy5 = cls("Gendy5")
Formant = cls("Formant")
Pulse = cls("Pulse")
LFPulse = cls("LFPulse")
PMOsc = cls("PMOsc")
Crackle = cls("Crackle")
LFCub = cls("LFCub")
PinkNoise = cls("PinkNoise")
Impulse = cls("Impulse")
Blip = cls("Blip")
Klank = cls("Klank", ref="`")
Resonz = cls("Resonz")
Squiz = cls("Squiz")

# Other

K2A = cls("K2A")
Out = cls("Out")
AudioIn = cls("AudioIn")
Lag = cls("Lag")
Vibrato = cls("Vibrato")
Line = cls("Line")
XLine = cls("XLine")
FreeVerb = cls("FreeVerb")
GVerb = cls("GVerb")
Pan2 = cls("Pan2")
LPF = cls("LPF")
RLPF = cls("RLPF")
BPF = cls("BPF")
HPF = cls("HPF")
RHPF = cls("RHPF")
DelayC = cls("DelayC")
DelayN = cls("DelayN")
DelayL = cls("DelayL")
CombN = cls("CombN")
CombL = cls("CombL")
CombC = cls("CombC")
Crackle = cls("Crackle")
Limiter = cls("Limiter")
Ringz = cls("Ringz")
Dust = cls("Dust")
Formlet = cls("Formlet")
ClipNoise = cls("ClipNoise")

BufRateScale = cls("BufRateScale")
BufSampleRate = cls("BufSampleRate")
BufFrames = cls("BufFrames")
BufChannels = cls("BufChannels")
BufFrames = cls("BufFrames")
BufDur = cls("BufDur")


# sc3 Plugins

BufGrain = cls("BufGrain")
Decimator = cls("Decimator")
SmoothDecimator = cls("SmoothDecimator")
CrossoverDistortion = cls("CrossoverDistortion")
Disintegrator = cls("Disintegrator")
MdaPiano = cls("MdaPiano")

# Array manipulation emulator functions


def stutter(array, n): return [item for item in array for i in range(n)]
def dup(x): return [x, x]