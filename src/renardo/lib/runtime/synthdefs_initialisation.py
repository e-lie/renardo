
from renardo.sc_backend import SCResourceType, SCInstrument, FileEffect, StartSoundEffect, MakeSoundEffect

from pathlib import Path

from renardo.gatherer import SCResourceFile
from renardo.lib.runtime.managers_instanciation import scresource_library
from renardo.settings_manager import settings

for scresource_bank in scresource_library:
    if scresource_bank.name in settings.get("sc_backend.ACTIVATED_SCCODE_BANKS"):
        for instrument_category in scresource_bank.instruments:
            for scresource_file in instrument_category:
                # load the SCInstrument instance declared in every python resource file found in library
                scinstrument = scresource_file.load_resource_from_python()
                pass
                # define a variable for each scinstrument (callable in the context of a player and returns a InstrumentProxy)
                globals()[scinstrument.shortname] = scinstrument

# create the special sccode dir in the user dir if not exist
Path(settings.get("sc_backend.SPECIAL_SCCODE_DIR")).mkdir(parents=True, exist_ok=True)

# The 1 or 2 channels buffer strategy of play (which is currently sending a channel error in SC so broken strategry) implies a specific setup with two players
play1_resource_file = SCResourceFile(
    path=Path(settings.get("sc_backend.SPECIAL_SCCODE_DIR")) / 'play1.py',
    resource_type=SCResourceType.INSTRUMENT,
    category="sampler"
)
play = play1_resource_file.load_resource_from_python()

play2_resource_file = SCResourceFile(
    path=Path(settings.get("sc_backend.SPECIAL_SCCODE_DIR")) / 'play2.py',
    resource_type=SCResourceType.INSTRUMENT,
    category="sampler"
)
play = play2_resource_file.load_resource_from_python()

# # add every effect for files found in library
# for scresource_bank in scresource_library:
#     if scresource_bank.name in settings.get("sc_backend.ACTIVATED_SCCODE_BANKS"):
#         for effect_category in scresource_bank.effects:
#             for scresource_file in effect_category:
#                 globals()[scresource_file.name] = FileEffect(sccode_path=scresource_file.path)


