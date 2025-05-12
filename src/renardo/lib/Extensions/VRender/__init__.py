from renardo.lib.Extensions.VRender.VRender import renderizeVoice
from renardo.lib.SynthDefManagement import DefaultPygenSynthDef
from renardo.runtime import Clock, Scale, Root
from renardo.settings_manager import settings

class VRenderSynthDef(DefaultPygenSynthDef):
    def __init__(self):
        DefaultPygenSynthDef.__init__(self, "vrender")
        self.add()

    def __call__(self, notes, pos=0, sample=0, **kwargs):

        if "lyrics" in kwargs:
            lyrics = kwargs['lyrics']
        else:
            lyrics = "oo "

        if "dur" in kwargs:
            durations = kwargs['dur']
        else:
            durations = [1]

        if 'file' in kwargs:
            filename = kwargs['file']
        else:
            filename = 'v1'

        if "sex" in kwargs:
            sex = kwargs["sex"]
        else:
            sex = "female"

        scale = list(Scale.default)
        tempo = int(Clock.bpm)

        notes = list(map(lambda x: x + Root.default,notes))

        renderizeVoice(filename,lyrics,notes,durations,tempo,scale,sex,settings.get("core.RENARDO_ROOT_PATH"))

vrender = VRenderSynthDef()