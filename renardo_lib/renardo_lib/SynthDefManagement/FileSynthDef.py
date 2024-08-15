from renardo_lib.Code import WarningMsg
from renardo_lib.SynthDefManagement import SynthDefProxy, DefaultSynthDef
from renardo_lib.SynthDefManagement.SynthDict import SynthDefs
from renardo_lib.ServerManager.default_server import Server
from renardo_lib.Settings import SYNTHDEF_DIR

class MinimalSynthDef(object):

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

    def load(self):
        """ Load in server"""
        return DefaultSynthDef.server.loadSynthDef(self.filename)

    def add(self):
        try:
            self.synth_added = True
            # Load to server
            #self.write()
            self.load()
        except Exception as e:
            WarningMsg("{}: SynthDef '{}' could not be added to the server:\n{}".format(e.__class__.__name__, self.name, e))
        return None


class FileSynthDef(MinimalSynthDef):

    def __str__(self):
        return open(self.filename, 'rb').read()
