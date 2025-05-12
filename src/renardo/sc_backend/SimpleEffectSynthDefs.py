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
from pathlib import Path

from renardo.lib.music_resource import Effect
from renardo.settings_manager import settings


class FileEffect(Effect):
    """Represents a SuperCollider effect loaded from a file."""

    def __init__(self, short_name, sccode_path, args={}):
        fullname = os.path.basename(sccode_path)
        super().__init__(
            shortname=short_name, 
            fullname=fullname, 
            description=f"Effect loaded from {fullname}",
            arguments=args
        )
        self.synthdef_fullname = sccode_path.name
        self.sccode_path = str(sccode_path)

    @classmethod
    def set_server(cls, server):
        cls.server = server

    def load(self):
        """Load the effect into the SuperCollider server."""
        return self.load_in_server()

    def load_in_server(self):
        """Load the effect from a file path."""
        if self.server is not None:
            self.server.loadSynthDef(self.sccode_path)
        return


class StartSoundEffect(FileEffect):
    """Special effect for starting sounds."""
    
    def __init__(self):
        FileEffect.__init__(
            self, 
            'startSound', 
            sccode_path=Path(settings.get_path("PLAY_SCCODE_DIR"))/'startSound.scd'
        )
        self.load()


class MakeSoundEffect(FileEffect):
    """Special effect for making sounds."""
    
    def __init__(self):
        self.max_duration = 8
        FileEffect.__init__(
            self, 
            'makeSound', 
            sccode_path=Path(settings.get_path("PLAY_SCCODE_DIR"))/'makeSound.scd'
        )
        self.load()

# -- TODO

# Have ordered effects e.g.
# 0. Process frequency / playback rate
# 1. Before envelope
# 2. Adding the envelope
# 3. After envelope