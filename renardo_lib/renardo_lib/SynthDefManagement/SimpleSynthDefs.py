import os
from renardo_lib.Code import WarningMsg
from renardo_lib.SynthDefManagement import SynthDefProxy
from renardo_lib.SynthDefManagement.SynthDict import SynthDefs
from renardo_lib.ServerManager.default_server import Server
from renardo_lib.Settings import SYNTHDEF_DIR, TMP_SYNTHDEF_DIR

class SimpleSynthDef(object):

    """
    Simplified Synthdef class that removes the dependencies to SCLang python bindings
    New mode of synthdef management for Renardo
    """

    server = Server
    bus_name = 'bus'
    synthdef_dict = SynthDefs

    def __init__(self, name):
        self.name = name
        self.synth_added = False
        self.filename     = SYNTHDEF_DIR + "/{}.scd".format(self.name)
        self.synthdef_dict[self.name] = self
        self.defaults = { "amp"       : 1,
                            "sus"       : 1,
                            "pan"       : 0,
                            "freq"      : 0,
                            "vib"       : 0,
                            "fmod"      : 0,
                            "rate"      : 0,
                            "bus"       : 0,
                            "blur"      : 1,
                            "beat_dur"  : 1,
                            "atk"       : 0.01,
                            "decay"     : 0.01,
                            "rel"       : 0.01,
                            "peak"      : 1,
                            "level"     : 0.8 }

    def __repr__(self):
        return str(self.name)

    def __call__(self, degree=None, **kwargs):
        return SynthDefProxy(self.name, degree, kwargs)

    def load_in_server_from_file(self):
        """ Load in server"""
        return SimpleSynthDef.server.loadSynthDef(self.filename)

    def add(self):
        try:
            self.synth_added = True
            # Load to server
            #self.write()
            self.load_in_server_from_file()
        except Exception as e:
            WarningMsg("{}: SynthDef '{}' could not be added to the server:\n{}".format(e.__class__.__name__, self.name, e))
        return None


class FileSynthDef(SimpleSynthDef):

    def __str__(self):
        return open(self.filename, 'rb').read()

class LiveSynthDef(SimpleSynthDef):

    """
    Lets livecode SClang synthdef directly as a string

    Example:

    newblip = LiveSynthDef(name="newblip")
    newblip.code('''
    arg amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, blur=1, beat_dur=1, atk=0.01, decay=0.01, rel=0.01, peak=1, level=0.8;
    var osc, env;
    sus = sus * blur;
    freq = In.kr(bus, 1);
    freq = [freq, freq+fmod];
    amp=(amp + 1e-05);
    freq=(freq + [0, LFNoise2.ar(50).range(-2, 2)]);
    freq=(freq * 2);
    osc=((LFCub.ar((freq * 1.002), iphase: 1.5) + (LFTri.ar(freq, iphase: Line.ar(2, 0, 0, 2)) * 0.3)) * Blip.ar((freq / 2), rate));
    osc=((osc * XLine.ar(amp, (amp / 10000), (sus * 2))) * 0.3);
    osc = Mix(osc) * 0.5;
    osc = Pan2.ar(osc, pan);
    ''')
    """

    def __init__(self, name, sccode=None, auto_add_synth=True):
        super(LiveSynthDef, self).__init__(name)
        self.filename     = TMP_SYNTHDEF_DIR + "/{}.scd".format(self.name)
        self.sccode = sccode
        if self.sccode:
            self.complete_code()
            if auto_add_synth:
                self.add()

    def complete_code(self):
        """
        This quick autocompletion allow to livecode only the core of the synthdef code.
        But if you want to code it completely with Synthdef.new and ReplaceOut
        it will leave it as is
        """
        if not "SynthDef.new" in self.sccode:
            self.sccode = f"SynthDef.new(\\{self.name},{{\n{self.sccode}"
        if not "ReplaceOut.ar" in self.sccode:
            self.sccode = f"{self.sccode}\nReplaceOut.ar(bus, osc)}}).add;"

    def code(self, sccode, auto_add_synth=True):
        self.sccode = sccode
        self.complete_code()
        if auto_add_synth:
            self.add()

    def write_tmp_file(self):
        try:
            with open(self.filename, 'w') as f:
                f.write(self.sccode)
        except IOError:
            pass
        return

    def add(self):
        try:
            self.synth_added = True
            self.write_tmp_file()
            self.load_in_server_from_file()

        except Exception as e:
            WarningMsg("{}: SynthDef '{}' could not be added to the server:\n{}".format(e.__class__.__name__, self.name, e))
        return None