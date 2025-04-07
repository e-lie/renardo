from renardo.sc_backend import LiveSynthDef, FileSynthDef, FileEffect, StartSoundEffect, MakeSoundEffect
from .python_defined_effect_synthdefs import effect_manager, PygenEffect, In, Out
from pathlib import Path
import tempfile

from renardo.gatherer import sccode_library
from renardo.settings_manager import settings

# define a variable for every instrument synthdef file found in library
for sccode_bank in sccode_library:
    if sccode_bank.name in settings.get("sc_backend.ACTIVATED_SCCODE_BANKS"):
        for instrument_category in sccode_bank.instruments:
            for sc_synth in instrument_category:
                os_temporary_dir = Path(tempfile.gettempdir())
                # Create a new file in the temporary directory
                scsynth_temporary_file = os_temporary_dir / f"{sc_synth.shortname}.scd"
                # Write sc code content to the file
                scsynth_temporary_file.write_text(sc_synth.code)
                globals()[sc_synth.shortname] = FileSynthDef(name=sc_synth.shortname, sccode_path=scsynth_temporary_file)

# create the special sccode dir in the user dir if not exist
Path(settings.get("sc_backend.PLAY_SCCODE_DIR")).mkdir(parents=True, exist_ok=True)

# The 1 or 2 channels buffer strategy of play (which is not working) implies a specific setup with two player
play = FileSynthDef('play1', Path(settings.get("sc_backend.PLAY_SCCODE_DIR")) / 'play1.scd')
play.defaults["dur"]=.5
play.add()
play = FileSynthDef('play2', Path(settings.get("sc_backend.PLAY_SCCODE_DIR")) / 'play2.scd')
play.defaults["dur"]=.5
play.add()

# add every effect for files found in library
for sccode_bank in sccode_library:
    if sccode_bank.name in settings.get("sc_backend.ACTIVATED_SCCODE_BANKS"):
        for effect_category in sccode_bank.effects:
            for sc_effect in effect_category:
                os_temporary_dir = Path(tempfile.gettempdir())
                # Create a new file in the temporary directory
                sceffect_temporary_file = os_temporary_dir / f"{sc_effect.shortname}.scd"
                # Write sc code content to the file
                sceffect_temporary_file.write_text(sc_effect.code)
                globals()[sc_effect.shortname] = FileEffect(short_name=sc_effect.shortname, sccode_path=sceffect_temporary_file, args=sc_effect.arguments)


