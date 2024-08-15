from renardo_lib.SCLang.SynthDef import SynthDefBaseClass


class SampleSynthDef(SynthDefBaseClass):
    def __init__(self, *args, **kwargs):
        SynthDefBaseClass.__init__(self, *args, **kwargs)
        self.buf = self.new_attr_instance("buf")
        self.pos = self.new_attr_instance("pos")
        self.defaults['buf']   = 0
        self.defaults['pos']   = 0
        self.defaults['room']  = 0.1
        self.defaults['rate']  = 1.0
        self.base.append("rate = In.kr(bus, 1);")
