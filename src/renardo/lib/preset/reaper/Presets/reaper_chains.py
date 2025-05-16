from renardo.reaper_backend.ReaperIntegration import init_reapy_project, ReaperInstrumentFactory, ReaTask

old_style_presets = {}

reaproject = init_reapy_project()
reainstru_factory = ReaperInstrumentFactory(old_style_presets, reaproject)
#reaper_instruments = reainstru_factory.create_all_facades_from_reaproject_tracks()

