from renardo.sc_backend.SimpleEffectSynthDefs import FileEffect, StartSoundEffect, MakeSoundEffect

class FileEffectManager(dict):
    def __init__(self):

        dict.__init__(self)
        self.kw = []
        self.all_kw = []
        self.defaults = {}
        self.order = {N: [] for N in range(3)}

    def __repr__(self):
        return "\n".join([repr(value) for value in self.values()])

    def values(self):
        return [self[key] for key in self.sort_by("synthdef")]

    def sort_by(self, attr):
        """ Returns the keys sorted by attribute name"""
        return sorted(self.keys(), key=lambda effect: getattr(self[effect], attr))

    def new(self, short_name_for_arg, sccode_path, args, order=2):
        self[short_name_for_arg] = FileEffect(short_name_for_arg, sccode_path, args)

        if order in self.order:
            self.order[order].append(short_name_for_arg)
        else:
            self.order[order] = [short_name_for_arg]

        # Store the main keywords together
        self.kw.append(short_name_for_arg)

        # Store other sub-keys
        for arg in args:
            if arg not in self.all_kw:
                self.all_kw.append(arg)
            # Store the default value
            self.defaults[arg] = args[arg]

        return self[short_name_for_arg]

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
            effect.load_in_server()
        StartSoundEffect()
        MakeSoundEffect()
        return


effect_manager = FileEffectManager()

Effects = effect_manager  # Alias - to become default