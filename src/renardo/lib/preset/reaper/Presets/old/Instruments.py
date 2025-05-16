from typing import Dict, List
from renardo.reaper_backend.ReaperIntegration import init_reapy_project, ReaperInstrumentFactory

#from .Presets import presets
from renardo.runtime import Clock, Scale
from functools import partial

Clock.midi_nudge = 0

old_style_presets = {}

reaproject = init_reapy_project()
reainstru_factory = ReaperInstrumentFactory(old_style_presets, reaproject)
reaper_instruments = reainstru_factory.create_all_facades_from_reaproject_tracks()

def newintru(name:str, plugin_name:str=None, effects:List=[], plugin_preset:str=None, params:Dict={}, scan_all_params:bool=False):
    if plugin_name is None:
        plugin_name = name
    if not params:
        scan_all_params = True
    instrument_facade = reainstru_factory.create_instrument_facade(name, plugin_name, plugin_preset, params, scan_all_params)
    for effect_config in effects:
        if isinstance(effect_config, dict):
            instrument_facade.add_effect_plugin(**effect_config)
        elif isinstance(effect_config, list):
            instrument_facade.add_effect_plugin(*effect_config)
    return instrument_facade.out, instrument_facade


for key, instrument_facade in reaper_instruments.items():
    globals()[key+'_facade'] = instrument_facade
    globals()[key] = instrument_facade.out



#
# try:
#     marimba = partial(mallets1, marimba_on=True, midi_map={' ':-200, '.': -200})
#     vibra = partial(mallets1, vibra_on=True, midi_map={' ':-200, '.': -200})
#     ceramic = partial(mallets1, ceramic_on=True, midi_map={' ':-200, '.': -200})
#
#     marimba2 = partial(mallets2, marimba_on=True, midi_map={' ':-200, '.': -200})
#     vibra2 = partial(mallets2, vibra_on=True, midi_map={' ':-200, '.': -200})
#     ceramic2 = partial(mallets2, ceramic_on=True, midi_map={' ':-200, '.': -200})
#
#     accciddd = partial(bass1, accciddd_on=True, midi_map={' ':-200, '.': -200})
#     hpluck = partial(bass1, hpluck_on=True, midi_map={' ':-200, '.': -200})
#     growlsid = partial(bass1, growlsid_on=True, midi_map={' ':-200, '.': -200})
#     darkpass = partial(bass1, darkpass_on=True, midi_map={' ':-200, '.': -200})
#     jupiter = partial(bass1, jupiter_on=True, midi_map={' ':-200, '.': -200})
#     madg = partial(bass1, madg_on=True, midi_map={' ':-200, '.': -200})
#
#     accciddd2 = partial(bass2, accciddd_on=True)
#     hpluck2 = partial(bass2, hpluck_on=True)
#     growlsid2 = partial(bass2, growlsid_on=True)
#     darkpass2 = partial(bass2, darkpass_on=True)
#     jupiter2 = partial(bass2, jupiter_on=True)
#     madg2 = partial(bass2, madg_on=True)
#
#     fordrip = partial(noises1, fordrip_on=True)
#     irise = partial(noises1, irise_on=True)
#     whibot = partial(noises1, whibot_on=True)
#     ratic = partial(noises1, ratic_on=True)
#     insiders = partial(noises1, insiders_on=True)
#
#     fordrip2 = partial(noises2, fordrip_on=True)
#     irise2 = partial(noises2, irise_on=True)
#     whibot2 = partial(noises2, whibot_on=True)
#     ratic2 = partial(noises2, ratic_on=True)
#     insiders2 = partial(noises2, insiders_on=True)
#
#     crazykit = partial(drumkit1, crazykit_on=True, scale=Scale.major)
#     kicker2 = partial(drumkit1, kicker_on=True)
#     rdrum = partial(drumkit1, rdrum_on=True)
#
#     crazykit2 = partial(drumkit2, crazykit_on=True, scale=Scale.major)
#     kicker = partial(drumkit2, kicker_on=True)
#     rdrum2 = partial(drumkit2, rdrum_on=True)
#
#     nlead = partial(synth1, nlead_on=True)
#     strpad = partial(synth1, strpad_on=True)
#     lofijoy = partial(synth1, lofijoy_on=True)
#     sheer = partial(synth1, sheer_on=True)
#     sloundge = partial(synth1, sloundge_on=True)
#     balimba = partial(synth1, balimba_on=True)
#     chicad = partial(synth1, chicad_on=True)
#
#     nlead2 = partial(synth2, nlead_on=True)
#     strpad2 = partial(synth2, strpad_on=True)
#     lofijoy2 = partial(synth2, lofijoy_on=True)
#     sheer2 = partial(synth2, sheer_on=True)
#     sloundge2 = partial(synth2, sloundge_on=True)
#     balimba2 = partial(synth2, balimba_on=True)
#     chicad2 = partial(synth2, chicad_on=True)
# except:
#     print("Error while initializing some instrument")


# mixer = ab.create_instrument(track_name="mixer", midi_channel=-1)
#
# sends = ab.create_instrument(track_name="sends", midi_channel=-1, set_defaults=False)
#
#
# metronome = ab.create_instrument(
#     track_name="metronome",
#     midi_channel=16,
#     set_defaults=False,
#     scale=Scale.chromatic,
#     oct=3,
#     config={"root": 0},
#     midi_map="stdrum",
# )
#
# # Channel 1
#
# kit808 = ab.create_instrument(
#     track_name="kit808",
#     midi_channel=1,
#     scale=Scale.chromatic,
#     oct=3,
#     config={"root": 0},
#     midi_map="stdrum",
#     dur=1 / 2,
# )
#
# kicker = ab.create_instrument(
#     track_name="kicker",
#     midi_channel=1,
#     config={"root": 0},
#     scale=Scale.chromatic,
#     oct=1.6,
#     midi_map="threesquare",
#     dur=1,
# )
#
# kitdatai = ab.create_instrument(
#     track_name="kitdatai",
#     midi_channel=1,
#     config={"root": 0},
#     scale=Scale.chromatic,
#     oct=4.4,
#     midi_map="stdrum",
#     dur=1 / 2,
# )
#
# # Channel 2
#
# kitcuba = ab.create_instrument(
#     track_name="_2",
#     midi_channel=2,
#     oct=3,
#     dur=1 / 2,
#     midi_map="stdrum",
#     config={
#         "root": 0,
#         "kitcuba_vol": 1,
#         "jazzkit_vol": 0,
#         "reaktorkit_vol": 0,
#         "harshkit_vol": 0,
#     },
#     scale=Scale.chromatic,
# )
#
# jazzkit = ab.create_instrument(
#     track_name="_2",
#     midi_channel=2,
#     oct=3,
#     dur=1 / 2,
#     midi_map="stdrum",
#     config={
#         "root": 0,
#         "kitcuba_vol": 0,
#         "jazzkit_vol": 1,
#         "reaktorkit_vol": 0,
#         "harshkit_vol": 0,
#     },
#     scale=Scale.chromatic,
# )
#
# reaktorkit = ab.create_instrument(
#     track_name="_2",
#     midi_channel=2,
#     oct=3,
#     dur=1 / 2,
#     midi_map="stdrum",
#     config={
#         "root": 0,
#         "kitcuba_vol": 0,
#         "jazzkit_vol": 0,
#         "reaktorkit_vol": 1,
#         "harshkit_vol": 0,
#     },
#     scale=Scale.chromatic,
# )
#
# harshkit = ab.create_instrument(
#     track_name="_2",
#     midi_channel=2,
#     oct=3,
#     dur=1 / 2,
#     midi_map="stdrum",
#     config={
#         "root": 0,
#         "kitcuba_vol": 0,
#         "jazzkit_vol": 0,
#         "reaktorkit_vol": 0,
#         "harshkit_vol": 1,
#     },
#     scale=Scale.chromatic,
# )
#
# # Channel 6
#
# crubass = ab.create_instrument(
#     track_name="_6",
#     midi_channel=6,
#     oct=3,
#     # sus=1/2, #the sustain bug disappeared
#     config={
#         "ubass_vol": 0,
#         "crubass_vol": 1,
#         "tb303_vol": 0,
#     }
#     | rndp(crubassp, 12),
# )
#
#
# tb303 = ab.create_instrument(
#     track_name="_6",
#     midi_channel=6,
#     oct=4,
#     # sus=1/2,
#     config={
#         "ubass_vol": 0,
#         "crubass_vol": 0,
#         "tb303_vol": 0.9,
#     },
# )
#
# ubass = ab.create_instrument(
#     track_name="_6",
#     midi_channel=6,
#     oct=4,
#     config={
#         "ubass_vol": 0.9,
#         "crubass_vol": 0,
#         "tb303_vol": 0,
#     },
# )
#
# # Channel 7
#
# crubass_2 = ab.create_instrument(
#     track_name="_7",
#     midi_channel=7,
#     oct=4,
#     config={
#         "ubass_vol": 0,
#         "crubass_vol": 1,
#         "tb303_vol": 0,
#     }
#     | rndp(crubassp, 12),
# )
#
# tb303_2 = ab.create_instrument(
#     track_name="_7",
#     midi_channel=7,
#     oct=4,
#     config={
#         "ubass_vol": 0,
#         "crubass_vol": 0,
#         "tb303_vol": 0.9,
#     },
# )
#
# # Channel 8
#
# piano = ab.create_instrument(
#     track_name="_8",
#     midi_channel=8,
#     oct=5,
#     config={
#         "piano_vol": 1,
#         "danceorg_vol": 0,
#     },
# )
#
# danceorg = ab.create_instrument(
#     track_name="_8",
#     midi_channel=8,
#     oct=5,
#     config={
#         "piano_vol": 0,
#         "danceorg_vol": 1,
#     },
# )
#
# kora = ab.create_instrument(
#     track_name="_4",
#     midi_channel=4,
#     oct=5,
#     config={
#         "kora_vol": 1,
#     },
# )
#
# strings = ab.create_instrument(
#     track_name="_9",
#     midi_channel=9,
#     oct=5,
#     config={
#         "strings_vol": 1,
#         "owstr_vol": 0,
#     },
# )
#
# owstr = ab.create_instrument(
#     track_name="_9",
#     midi_channel=9,
#     oct=5,
#     config={
#         "strings_vol": 0,
#         "owstr_vol": 1,
#     },
# )
#
# balafon = ab.create_instrument(
#     track_name="_10",
#     midi_channel=10,
#     oct=5,
#     config={
#         "balafon_vol": 1,
#         "bells_vol": 0,
#     },
# )
#
# bells = ab.create_instrument(
#     track_name="_10",
#     midi_channel=10,
#     oct=5,
#     config={
#         "balafon_vol": 0,
#         "bells_vol": 1,
#     },
# )
