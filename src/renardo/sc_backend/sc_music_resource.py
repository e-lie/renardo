"""
SuperCollider music resource implementations for Renardo.

This module provides SuperCollider-specific implementations of the 
generic music resource classes from renardo.lib.music_resource.
"""


import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

from renardo.lib.InstrumentProxy import InstrumentProxy
from renardo.lib.music_resource import Instrument, Effect, ResourceType
from renardo.settings_manager import settings


class SCEffect(Effect):
    """Represents a SuperCollider effect processor."""

    def __init__(
            self,
            shortname: str,
            code: str,
            fullname: Optional[str] = None,
            description: Optional[str] = None,
            arguments: Dict[str, Any] = None,
            bank: str = "undefined",
            category: str = "undefined",
            order=2,
    ):
        super().__init__(shortname, fullname, description, arguments, bank, category, order)
        self.code = code  # SuperCollider language code

    @classmethod
    def set_server(cls, server):
        cls.server = server

    def load(self):
        """Load the effect in the SuperCollider server"""
        return self.load_in_server_from_tempfile()

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


class SCInstrument(Instrument):
    """Represents a SuperCollider synthesizer instrument."""

    bus_name = 'bus'

    def __init__(
            self,
            shortname: str,
            code: str,
            fullname: Optional[str] = None,
            description: Optional[str] = None,
            arguments: Dict[str, Any] = None,
            bank: str = "undefined",
            category: str = "undefined",
            auto_load_to_server: bool = True,
    ):
        super().__init__(shortname, fullname, description, arguments, bank, category)
        self.code = code  # SuperCollider language code
        self.synth_added = False

        self.synthdef_dict[self.shortname] = self

        if auto_load_to_server:
            self.load()

    @classmethod
    def set_server(cls, server):
        cls.server = server

    @classmethod
    def set_instrument_dict(cls, synthdef_dict):
        cls.synthdef_dict = synthdef_dict

    @classmethod
    def set_buffer_manager(cls, buffer_manager):
        cls.buffer_manager = buffer_manager

    def __call__(self, first_argument=None, **kwargs):
        # "loop" and similar instruments use a different
        # function signature : first arg is filename and not degree
        instrument_proxy = None

        # standard handling of default argument values in the parent method
        kwargs = self.merge_with_defaults(**kwargs)

        if self.shortname in ["loop", "stretch"]:
            filename = first_argument
            pos = kwargs["pos"] if "pos" in kwargs.keys() else 0
            sample = kwargs["sample"] if "sample" in kwargs.keys() else 0
            instrument_proxy = InstrumentProxy(self.shortname, pos, kwargs)
            instrument_proxy.kwargs["filename"] = filename
            instrument_proxy.kwargs["buf"] = SCInstrument.buffer_manager.load_buffer(filename, sample)
        elif self.shortname in ["granular"]: # to debug
            filename = first_argument
            pos = kwargs["pos"] if "pos" in kwargs.keys() else 0
            sample = kwargs["sample"] if "sample" in kwargs.keys() else 0
            kwargs["buf"] = SCInstrument.buffer_manager.load_buffer(filename, sample)
            instrument_proxy = InstrumentProxy(self.shortname, pos, kwargs)
        else:
            degree = first_argument
            instrument_proxy = InstrumentProxy(self.shortname, degree, kwargs)
        return instrument_proxy


    def load(self):
        """Load the instrument in the SuperCollider server"""
        return self.load_in_server_from_tempfile()

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
        self.sccode = self.code  # Initialize sccode with code content
        if not "SynthDef.new" in self.code:
            self.sccode = f"SynthDef.new(\\{self.shortname},{{\n{self.code}"
        if not "ReplaceOut.ar" in self.sccode:
            self.sccode = f"{self.sccode}\nReplaceOut.ar(bus, osc)}}).add;"