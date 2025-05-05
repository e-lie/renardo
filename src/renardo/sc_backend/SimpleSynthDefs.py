import tempfile
from enum import Enum
from pathlib import Path
from typing import Dict, Any
from renardo.sc_backend.InstrumentProxy import InstrumentProxy
from renardo.settings_manager import settings

class SCResourceType(Enum):
    INSTRUMENT = "instrument"
    EFFECT = "effect"

class SCResource:
    """Base class for SuperCollider resources (synths and effects)."""

    def __init__(
            self,
            shortname: str,
            fullname: str,
            description: str,
            code: str,
            arguments: Dict[str, Any] = None
    ):
        self.shortname = shortname
        self.fullname = fullname
        self.description = description
        self.code = code  # SuperCollider language code as a multiline string
        self.arguments = arguments or {}

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.shortname}, {len(self.arguments)} args)"

    def __repr__(self) -> str:
        return self.__str__()

class SCEffect(SCResource):
    """Represents a SuperCollider effect processor."""

    def __init__(
            self,
            shortname: str,
            fullname: str,
            description: str,
            code: str,
            arguments: Dict[str, Any] = None,
            bank: str = "undefined",
            category: str = "undefined",
            order=2,
    ):
        super().__init__(shortname, fullname, description, code, arguments)
        self.bank = bank
        self.category = category
        self.order=order
        self.args=arguments
        self.defaults=arguments

    def __str__(self) -> str:
        return f"SCEffect({self.shortname}, {len(self.arguments)} args)"

    @classmethod
    def set_server(cls, server):
        cls.server = server

    def __repr__(self):
        # return "<Fx '{}' -- args: {}>".format(self.synthdef, ", ".join(self.args))
        other_args = ['{}'.format(arg)
                      for arg in self.arguments if arg != self.shortname]
        other_args = ", other args={}".format(other_args) if other_args else ""
        return "<'{}': keyword='{}'{}>".format(self.fullname, self.shortname, other_args)

    # def doc(self, string):
    #     """ Set a docstring for the effects"""
    #     return

    def load_in_server_from_tempfile(self):
        """ Load resource in SuperCollider server"""
        try:
            scd_temporary_dir = Path(tempfile.gettempdir()) / "renardo" / self.bank / "effects"
            # Create a new file in the temporary directory
            scd_temporary_dir.mkdir(parents=True, exist_ok=True)
            sceffects_temporary_file = scd_temporary_dir / f"{self.shortname}.scd"
            # Write sc code content to the file
            sceffects_temporary_file.write_text(self.code)
            self.server.loadSynthDef(str(sceffects_temporary_file))
        except Exception as e:
            print(f"{e.__class__.__name__}: Effect '{self.shortname}' could not be added to the server:\n{e}")
        return None



class SCInstrument(SCResource):
    """Represents a SuperCollider synthesizer instrument."""

    #server = Server
    bus_name = 'bus'
    #synthdef_dict = SynthDefs

    def __init__(
            self,
            shortname: str,
            fullname: str,
            description: str,
            code: str,
            arguments: Dict[str, Any] = None,
            bank: str = "undefined",
            category: str = "undefined",
            auto_load_to_server: bool = False,
    ):
        super().__init__(shortname, fullname, description, code, arguments)
        self.category = category
        self.bank = bank
        self.name = self.shortname # old alias to remove
        self.synth_added = False

        self.synthdef_dict[self.shortname] = self

        #TODO merge with arguments and clarify how this is used later
        self.defaults = {"amp": 1,
                         "sus": 1,
                         "pan": 0,
                         "freq": 0,
                         "vib": 0,
                         "fmod": 0,
                         "rate": 0,
                         "bus": 0,
                         "blur": 1,
                         "beat_dur": 1,
                         "atk": 0.01,
                         "decay": 0.01,
                         "rel": 0.01,
                         "peak": 1,
                         "level": 0.8}

        if auto_load_to_server:
            self.load_in_server_from_tempfile()

    @classmethod
    def set_server(cls, server):
        cls.server = server

    @classmethod
    def set_instrument_dict(cls, synthdef_dict):
        cls.synthdef_dict = synthdef_dict

    @classmethod
    def set_buffer_manager(cls, buffer_manager):
        cls.buffer_manager = buffer_manager

    def __str__(self) -> str:
        return f"SCInstrument({self.shortname}, {len(self.arguments)} args)"

    def __repr__(self):
        return str(self.shortname)

    def __call__(self, first_argument=None, **kwargs):
        # "loop" and similar instruments use a different
        #function signature : first arg is filename and not degree
        if self.shortname in ["loop", "stretch"]:
            filename = first_argument
            pos = kwargs["pos"] if "pos" in kwargs.keys() else 0
            sample = kwargs["sample"] if "sample" in kwargs.keys() else 0
            proxy = InstrumentProxy(self.shortname, pos, kwargs)
            proxy.kwargs["filename"] = filename
            proxy.kwargs["buf"] = SCInstrument.buffer_manager.load_buffer(filename, sample)
            return proxy
        elif self.shortname in ["granular"]: # to debug
            filename = first_argument
            pos = kwargs["pos"] if "pos" in kwargs.keys() else 0
            sample = kwargs["sample"] if "sample" in kwargs.keys() else 0
            kwargs["buf"] = SCInstrument.buffer_manager.load_buffer(filename, sample)
            return InstrumentProxy(self.shortname, pos, kwargs)
        else:
            degree = first_argument
            return InstrumentProxy(self.shortname, degree, kwargs)

    def load_in_server_from_tempfile(self):
        """ Load resource in SuperCollider server"""
        try:
            # use os specific temporary dir to save scd files to load
            scd_temporary_dir = Path(tempfile.gettempdir()) / "renardo" / self.bank / "instruments"
            # Create a new file in the temporary directory
            scd_temporary_dir.mkdir(parents=True, exist_ok=True)
            scinstrument_temporary_file = scd_temporary_dir / f"{self.shortname}.scd"
            # Write sc code content to the file
            scinstrument_temporary_file.write_text(self.code)
            self.synth_added = True
            return SCInstrument.server.loadSynthDef(str(scinstrument_temporary_file))
        except Exception as e:
            print(f"{e.__class__.__name__}: SynthDef '{self.shortname}' could not be added to the server:\n{e}")
        return None

    def complete_code(self):
        """
        This quick autocompletion allow to livecode only the core of the synthdef code.
        But if you want to code it completely with Synthdef.new and ReplaceOut
        it will leave it as is
        """
        if not "SynthDef.new" in self.code:
            self.sccode = f"SynthDef.new(\\{self.shortname},{{\n{self.code}"
        if not "ReplaceOut.ar" in self.sccode:
            self.sccode = f"{self.sccode}\nReplaceOut.ar(bus, osc)}}).add;"


# class LiveSynthDef(SCInstrument):

#     """
#     Lets livecode SClang synthdef directly as a string

#     Example:

#     newblip = LiveSynthDef(name="newblip")
#     newblip.code('''
#     arg amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, blur=1, beat_dur=1, atk=0.01, decay=0.01, rel=0.01, peak=1, level=0.8;
#     var osc, env;
#     sus = sus * blur;
#     freq = In.kr(bus, 1);
#     freq = [freq, freq+fmod];
#     amp=(amp + 1e-05);
#     freq=(freq + [0, LFNoise2.ar(50).range(-2, 2)]);
#     freq=(freq * 2);
#     osc=((LFCub.ar((freq * 1.002), iphase: 1.5) + (LFTri.ar(freq, iphase: Line.ar(2, 0, 0, 2)) * 0.3)) * Blip.ar((freq / 2), rate));
#     osc=((osc * XLine.ar(amp, (amp / 10000), (sus * 2))) * 0.3);
#     osc = Mix(osc) * 0.5;
#     osc = Pan2.ar(osc, pan);
#     ''')
#     """

#     def __init__(self, name, sccode=None, auto_add_synth=True):
#         super(LiveSynthDef, self).__init__(name, sccode_path=settings.get("sc_backend.TMP_SYNTHDEF_DIR") + "/{}.scd".format(self.name))
#         self.sccode = sccode
#         if self.sccode:
#             self.complete_code()
#             if auto_add_synth:
#                 self.add()

#     def complete_code(self):
#         """
#         This quick autocompletion allow to livecode only the core of the synthdef code.
#         But if you want to code it completely with Synthdef.new and ReplaceOut
#         it will leave it as is
#         """
#         if not "SynthDef.new" in self.sccode:
#             self.sccode = f"SynthDef.new(\\{self.name},{{\n{self.sccode}"
#         if not "ReplaceOut.ar" in self.sccode:
#             self.sccode = f"{self.sccode}\nReplaceOut.ar(bus, osc)}}).add;"

#     def code(self, sccode, auto_add_synth=True):
#         self.sccode = sccode
#         self.complete_code()
#         if auto_add_synth:
#             self.add()

#     def write_tmp_file(self):
#         try:
#             with open(self.sccode_path, 'w') as f:
#                 f.write(self.sccode)
#         except IOError:
#             pass
#         return

#     def add(self):
#         try:
#             self.synth_added = True
#             self.write_tmp_file()
#             self.load_in_server_from_tempfile()

#         except Exception as e:
#             WarningMsg("{}: SynthDef '{}' could not be added to the server:\n{}".format(e.__class__.__name__, self.name, e))
#         return None