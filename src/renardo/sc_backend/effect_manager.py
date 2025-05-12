from renardo.sc_backend.sc_music_resource import SCEffect
from renardo.sc_backend.SimpleEffectSynthDefs import StartSoundEffect, MakeSoundEffect

class EffectManager(dict):
    def __init__(self):

        dict.__init__(self)
        self.kw = []
        self.all_kw = []
        self.defaults = {}
        self.order = {N: [] for N in range(3)}

    def __repr__(self):
        return "\n".join([repr(value) for value in self.values()])

    def values(self):
        return [self[key] for key in self.sort_by("fullname")]

    def sort_by(self, attr):
        """ Returns the keys sorted by attribute name"""
        return sorted(self.keys(), key=lambda effect: getattr(self[effect], attr))

    def new(self, sceffect:SCEffect):
        self[sceffect.shortname] = sceffect
        sceffect.load_in_server_from_tempfile()
        order = sceffect.order
        if order in self.order:
            self.order[order].append(sceffect.shortname)
        else:
            self.order[order] = [sceffect.shortname]
        # Store the main keywords together
        self.kw.append(sceffect.shortname)
        # Store other sub-keys
        for arg in sceffect.arguments:
            if arg not in self.all_kw:
                self.all_kw.append(arg)
            # Store the default value
            self.defaults[arg] = sceffect.arguments[arg]
        return self[sceffect.shortname]

    def kwargs(self):
        """ Returns the title keywords for each effect """
        return tuple(self.kw)

    def all_kwargs(self):
        """ Returns *all* keywords for all effects """
        return tuple(self.all_kw)

    def __iter__(self):
        for key in self.kw:
            yield key, self[key]

    def reload(self):
        """ Re-sends each effect to SC """
        for kw, effect in self:
            effect.load_in_server_from_tempfile()
        StartSoundEffect()
        MakeSoundEffect()
        return


