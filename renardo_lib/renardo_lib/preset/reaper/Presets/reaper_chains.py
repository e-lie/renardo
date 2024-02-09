from FoxDot.lib.Extensions.ReaperIntegration import init_reapy_project, ReaperInstrumentFactory, ReaTask

old_style_presets = {}

reaproject = init_reapy_project()
reainstru_factory = ReaperInstrumentFactory(old_style_presets, reaproject)
#reaper_instruments = reainstru_factory.create_all_facades_from_reaproject_tracks()

add_chains = reainstru_factory.add_chains
instanciate = reainstru_factory.instanciate