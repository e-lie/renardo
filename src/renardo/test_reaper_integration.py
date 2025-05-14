

from renardo.runtime import *

from renardo.reaper_backend.ReaperIntegration import init_reapy_project, ReaperInstrumentFactory

old_style_presets = {}

import renardo_reapy.runtime as reany
import renardo_reapy.reascript_api as RPR

RPR.ShowConsoleMsg("coucou")

reaproject = init_reapy_project()

reainstru_factory = ReaperInstrumentFactory(old_style_presets, reaproject)

add_chains = reainstru_factory.add_chains
instanciate = reainstru_factory.instanciate




gone = instanciate("chan1", "pads/gone_1")
# gonec = instanciate("chan1", "effects/limit2_0")
# bass303 = instanciate("chan2", "bass/bass303_2")
# bass303c = instanciate("chan2", "effects/limit2_0")

g1 = Player()
g1 >> gone(0)

pass