from renardo.reaper_backend.ReaperIntegration import init_reapy_project
from renardo.reaper_backend.reaper_music_resource import ReaperInstrument

old_style_presets = {}

reaproject = init_reapy_project()

ReaperInstrument.initialize_factory(
    presets=old_style_presets,
    project=reaproject
)

#reainstru_factory = ReaperInstrumentFactory(old_style_presets, reaproject)
#reaper_instruments = reainstru_factory.create_all_facades_from_reaproject_tracks()
