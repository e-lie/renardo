
from renardo.lib.music_resource import ResourceType
from renardo.sc_backend import SCInstrument, SCEffect
from renardo.sc_backend import FileEffect, StartSoundEffect, MakeSoundEffect

from pathlib import Path

from renardo.gatherer import SCResourceFile
from renardo.runtime.managers_instanciation import scresource_library, effect_manager, Server
from renardo.settings_manager import settings
from renardo.lib.Code import WarningMsg

for scresource_bank in scresource_library:
    if scresource_bank.name in settings.get("sc_backend.ACTIVATED_SCCODE_BANKS"):
        for instrument_category in scresource_bank.instruments:
            for scresource_file in instrument_category:
                try:
                    # load the SCInstrument instance declared in every python resource file found in library
                    scinstrument:SCInstrument = scresource_file.load_resource_from_python()
                    scinstrument.bank = scresource_bank.name
                    scinstrument.category = instrument_category.category
                    scinstrument.load_in_server_from_tempfile()
                    # define a variable for each scinstrument (callable in the context of a player and returns a InstrumentProxy)
                    globals()[scinstrument.shortname] = scinstrument
                except Exception as e:
                    print(f"Resource from {scresource_file.path} could not be loaded : {e}")


# create the special sccode dir in the user dir if not exist
settings.get_path("SPECIAL_SCCODE_DIR").mkdir(parents=True, exist_ok=True)

# The 1 or 2 channels buffer strategy of play (which is currently sending a channel error in SC so broken strategry) implies a specific setup with two players
play1_resource_file = SCResourceFile(
    path=settings.get_path("SPECIAL_SCCODE_DIR") / 'play1.py',
    resource_type=ResourceType.INSTRUMENT,
    category="sampler"
)
play = play1_resource_file.load_resource_from_python()

play2_resource_file = SCResourceFile(
    path=settings.get_path("SPECIAL_SCCODE_DIR") / 'play2.py',
    resource_type=ResourceType.INSTRUMENT,
    category="sampler"
)
play = play2_resource_file.load_resource_from_python()

# # add every effect for files found in library
for scresource_bank in scresource_library:
    if scresource_bank.name in settings.get("sc_backend.ACTIVATED_SCCODE_BANKS"):
        for effect_category in scresource_bank.effects:
            for scresource_file in effect_category:
                try:
                    # load the SCInstrument instance declared in every python resource file found in library
                    sceffect = scresource_file.load_resource_from_python()
                    sceffect.bank = scresource_bank.name
                    sceffect.category = effect_category.category
                    effect_manager.new(sceffect)
                except Exception as e:
                    print(f"Resource from {scresource_file.path} could not be loaded : {e}")