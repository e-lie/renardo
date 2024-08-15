from renardo_lib.SynthDefManagement.BufferManagement import Samples
from renardo_lib.SynthDefManagement.SCLangExperimentalPythonBindings.PygenSynthDef import PygenSynthDefBaseClass
from renardo_lib.Settings import SAMPLES_PACK_NUMBER


class SamplePygenSynthDef(PygenSynthDefBaseClass):
    def __init__(self, *args, **kwargs):
        PygenSynthDefBaseClass.__init__(self, *args, **kwargs)
        self.buf = self.new_attr_instance("buf")
        self.pos = self.new_attr_instance("pos")
        self.defaults['buf']   = 0
        self.defaults['pos']   = 0
        self.defaults['room']  = 0.1
        self.defaults['rate']  = 1.0
        self.base.append("rate = In.kr(bus, 1);")


class LoopPygenSynthDef(SamplePygenSynthDef):
    def __init__(self):
        SamplePygenSynthDef.__init__(self, "loop")
        self.pos = self.new_attr_instance("pos")
        self.sample = self.new_attr_instance("sample")
        self.spack = self.new_attr_instance("spack")
        self.beat_stretch = self.new_attr_instance("beat_stretch")
        self.defaults['pos']   = 0
        self.defaults['sample']   = 0
        self.defaults['spack'] = SAMPLES_PACK_NUMBER
        self.defaults['beat_stretch'] = 0
        self.base.append("rate = (rate * (1-(beat_stretch>0))) + ((BufDur.kr(buf) / sus) * (beat_stretch>0));")
        self.base.append("osc = PlayBuf.ar(2, buf, BufRateScale.kr(buf) * rate, startPos: BufSampleRate.kr(buf) * pos, loop: 1.0);")
        self.base.append("osc = osc * EnvGen.ar(Env([0,1,1,0],[0.05, sus-0.05, 0.05]));")
        self.osc = self.osc * self.amp
        self.add()
    def __call__(self, filename, pos=0, sample=0, **kwargs):
        kwargs["buf"] = Samples.loadBuffer(filename, sample)
        proxy = SamplePygenSynthDef.__call__(self, pos, **kwargs)
        proxy.kwargs["filename"] = filename
        return proxy


class StretchPygenSynthDef(SamplePygenSynthDef):
    def __init__(self):
        SamplePygenSynthDef.__init__(self, "stretch")
        self.base.append("osc = Warp1.ar(2, buf, Line.kr(0,1,sus), rate, windowSize: 0.2, overlaps: 4, interp:2);")
        self.base.append("osc = osc * EnvGen.ar(Env([0,1,1,0],[0.05, sus-0.05, 0.05]));")
        self.osc = self.osc * self.amp
        self.add()
    def __call__(self, filename, pos=0, sample=0, **kwargs):
        kwargs["buf"] = Samples.loadBuffer(filename, sample)
        proxy = SamplePygenSynthDef.__call__(self, pos, **kwargs)
        proxy.kwargs["filename"] = filename
        return proxy


class GranularPygenSynthDef(SamplePygenSynthDef):
    def __init__(self):
        SamplePygenSynthDef.__init__(self, "gsynth")
        self.pos = self.new_attr_instance("pos")
        self.sample = self.new_attr_instance("sample")
        self.defaults['pos']   = 0
        self.defaults['sample']   = 0
        self.defaults['spack'] = SAMPLES_PACK_NUMBER
        self.base.append("osc = PlayBuf.ar(2, buf, BufRateScale.kr(buf) * rate, startPos: BufSampleRate.kr(buf) * pos);")
        self.base.append("osc = osc * EnvGen.ar(Env([0,1,1,0],[0.05, sus-0.05, 0.05]));")
        self.osc = self.osc * self.amp
        self.add()
    def __call__(self, filename, pos=0, sample=0, **kwargs):
        kwargs["buf"] = Samples.loadBuffer(filename, sample)
        return SamplePygenSynthDef.__call__(self, pos, **kwargs)

