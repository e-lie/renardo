"""
    Filter Effects
    --------------

    Effects are added to Player objects as keywords instructions like `dur`
    or `amp` but are a little more tricky. Each effect has a "title" keyword,
    which requires a nonzero value to add the effect to a Player. Effects
    also have other attribute keywords which can be any value and may have
    a default value which is set when a Player is created.

    ::
        # Example. Reverb effect "title" is `room` and attribute is `mix`, which
        # defaults to 0.25. The following adds a reverb effect

        p1 >> pads(room=0.5)

        # This still adds the effect, but a mix of 0 doesn't actually do anything

        p1 >> pads(room=0.5, mix=0)

        # This effect is not added as the "title" keyword, room, is 0

        p1 >> pads(room=0, mix=0.5)

    Other effects are outlined below:

    *High Pass Filter* - Title keyword: `hpf`, Attribute keyword(s): `hpr`
    Only frequences **above** the value of `hpf` are kept in the final signal. Use `hpr` to set the resonance (usually a value between 0 and 1)

    *Low Pass Filter* - Title keyword: `lpf`, Attribute keyword(s): `lpr`
    Only frequences **below** the value of `lpf` are kept in final signal. Use `lpr` to set the resonance (usually a value between 0 and 1)

    *Bitcrush* - Title keyword: `bits`, Attribute keyword(s): `crush`
    The bit depth, in number of `bits`, that the signal is reduced to; this is a value between 1 and 24 where other values are ignored. Use `crush` to set the amount of reduction to the bitrate (defaults to 8)

    *Reverb* - Title keyword: `room`, Attribute keyword(s): `mix`
    The `room` argument specifies the size of the room and `mix` is the dry/wet mix of reverb; this should be a value between 0 and 1 (defalts to 0.25)

    *Chop* - Title keyword: `chop`, Attribute keyword(s): `sus`
    'Chops' the signal into chunks using a low frequency pulse wave over the sustain of a note.

    *Slide To* - Title keyword: `slide`, Attribute keyword(s):
    Slides' the frequency value of a signal to `freq * (slide+1)` over the  duration of a note (defaults to 0)

    *Slide From* - Title keyword: `slidefrom`, Attribute keyword(s):
    Slides' the frequency value of a signal from `freq * (slidefrom)` over the  duration of a note (defaults to 1)

    *Comb delay (echo)* - Title keyword: `echo`, Attribute keyword(s): `decay`
    Sets the decay time for any echo effect in beats, works best on Sample Player (defaults to 0)

    *Panning* - Title keyword: `pan`, Attribute keyword(s):
    Panning, where -1 is far left, 1 is far right (defaults to 0)

    *Vibrato* - Title keyword: `vib`, Attribute keyword(s):
    Vibrato (defaults to 0)

    Undocumented: Spin, Shape, Formant, BandPassFilter, Echo


"""

import os.path
from renardo.settings_manager import settings


class PygenEffect:

    server = None

    def __init__(self, short_name, synthdef_fullname, args={}, control=False):

        #self.server =Server
        self.short_name = short_name
        self.synthdef_fullname = synthdef_fullname
        self.file_path = str(settings.get_path("TMP_EFFECTS_DIR")) + "/{}.scd".format(self.synthdef_fullname)
        self.args = args.keys()
        self.vars = ["osc"]
        self.defaults = args
        self.effect_code_lines = []
        self.control = control

        self.suffix = "kr" if self.control else "ar"
        self.channels = 1 if self.control else 2

        self.input = "osc = In.{}(bus, {});\n".format(
            self.suffix, self.channels)
        self.output = "ReplaceOut.{}".format(self.suffix)

    @classmethod
    def set_server(cls, server):
        cls.server = server

    def __repr__(self):
        # return "<Fx '{}' -- args: {}>".format(self.synthdef, ", ".join(self.args))
        other_args = ['{}'.format(arg)
                      for arg in self.args if arg != self.short_name]
        other_args = ", other args={}".format(other_args) if other_args else ""
        return "<'{}': keyword='{}'{}>".format(self.synthdef_fullname, self.short_name, other_args)

    def __str__(self):
        s = "SynthDef.new(\\{},\n".format(self.synthdef_fullname)
        s += "{" + "|bus, {}|\n".format(", ".join(self.args))
        s += "var {};\n".format(",".join(self.vars))
        s += self.input
        s += self.list_effect_lines()
        s += self.output
        s += "(bus, osc)}).add;"
        return s

    def add_effect_line(self, string):
        self.effect_code_lines.append(string)
        return

    def doc(self, string):
        """ Set a docstring for the effects"""
        return

    def list_effect_lines(self):
        s = ""
        for p in self.effect_code_lines:
            s += p + ";\n"
        return s

    def add_var(self, name):
        if name not in self.vars:
            self.vars.append(name)
        return

    def add(self):
        ''' writes to file and sends to server '''
        # 1. See if the file exists
        if os.path.isfile(self.file_path):
            with open(self.file_path) as f:
                contents = f.read()
        else:
            contents = ""
        # 2. If it does, check contents
        this_string = self.__str__()
        if contents != this_string:
            try:
                with open(self.file_path, 'w') as f:
                    f.write(this_string)
            except IOError:
                print("IOError: Unable to update '{}' effect.".format(self.synthdef_fullname))
        # 3. Send to server
        self.load_in_server()

    def load_in_server(self):
        """ Load the Effect """
        if self.server is not None:
            self.server.loadSynthDef(self.file_path)
        return

class In(PygenEffect):
    def __init__(self):
        PygenEffect.__init__(self, 'startSound', 'startSound')
        self.add()

    def __str__(self):
        s = "SynthDef.new(\\startSound,\n"
        s += "{ arg bus, rate=1, sus; var osc;\n"
        s += "	ReplaceOut.kr(bus, rate)}).add;\n"
        return s


class Out(PygenEffect):
    def __init__(self):
        self.max_duration = 8
        PygenEffect.__init__(self, 'makeSound', 'makeSound')
        self.add()

    def __str__(self):
        s = "SynthDef.new(\\makeSound,\n"
        s += "{ arg bus, sus; var osc;\n"
        s += "	osc = In.ar(bus, 2);\n"
        s += "  osc = EnvGen.ar(Env([1,1,0],[sus * {}, 0.1]), doneAction: 14) * osc;\n".format(
            self.max_duration)
        s += "	DetectSilence.ar(osc, amp:0.0001, time: 0.1, doneAction: 14);\n"
        #s += "	Out.ar(0, osc);\n"
        s += "OffsetOut.ar(0, osc[0]);\n"
        s += "OffsetOut.ar(1, osc[1]);\n"
        s += " }).add;\n"
        return s

# -- TODO

# Have ordered effects e.g.
# 0. Process frequency / playback rate
# 1. Before envelope
# 2. Adding the envelope
# 3. After envelope

