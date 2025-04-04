from renardo.sc_backend import LiveSynthDef, FileSynthDef
from .python_defined_effect_synthdefs import effect_manager, PygenEffect, In, Out
from pathlib import Path

from renardo.gatherer import sccode_library
from renardo.settings_manager import settings

# define a variable for every instrument synthdef file found in library
for sccode_bank in sccode_library:
    if sccode_bank.name in settings.get("sc_backend.ACTIVATED_SCCODE_BANKS"):
        pass
        for instrument_category in sccode_bank.instruments:
            for sccode_file in instrument_category:
                globals()[sccode_file.name] = FileSynthDef(name=sccode_file.name, sccode_path=sccode_file.path)

# create the special sccode dir in the user dir if not exist
Path(settings.get("sc_backend.PLAY_SCCODE_DIR")).mkdir(parents=True, exist_ok=True)

# The 1 or 2 channels buffer strategy of play (which is not working) implies a specific setup with two player
play = FileSynthDef('play1', Path(settings.get("sc_backend.PLAY_SCCODE_DIR")) / 'play1.scd')
play.defaults["dur"]=.5
play.add()
play = FileSynthDef('play2', Path(settings.get("sc_backend.PLAY_SCCODE_DIR")) / 'play2.scd')
play.defaults["dur"]=.5
play.add()


