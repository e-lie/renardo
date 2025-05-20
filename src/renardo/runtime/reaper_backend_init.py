# from renardo.reaper_backend.reaper_music_resource import ReaperInstrument

#reainstru_factory = ReaperInstrumentFactory(old_style_presets, reaproject)
#reaper_instruments = reainstru_factory.create_all_facades_from_reaproject_tracks()

from renardo.runtime.managers_instanciation import reaper_resource_library
from renardo.reaper_backend import ReaperInstrument
from renardo.settings_manager import settings

num_channels_used = 0

for reaper_resource_bank in reaper_resource_library:
    if reaper_resource_bank.name in settings.get("reaper_backend.ACTIVATED_REAPER_BANKS"):
        for instrument_category in reaper_resource_bank.instruments:
            for reaper_resource_file in instrument_category:
                if not num_channels_used >= 16:
                    num_channels_used += 1
                    # load the SCInstrument instance declared in every python resource file found in library
                    reaper_instrument:ReaperInstrument = reaper_resource_file.load_resource_from_python()
                    reaper_instrument.bank = reaper_resource_bank.name
                    reaper_instrument.category = instrument_category.category
                    if reaper_instrument:
                        # define a variable for each scinstrument (callable in the context of a player and returns a InstrumentProxy)
                        globals()[reaper_instrument.shortname] = reaper_instrument
                    else:
                        print(f"resource from {reaper_resource_file.path} could not be loaded !")
                else:
                    break