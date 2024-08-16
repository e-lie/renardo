from renardo_lib.SynthDefManagement.SCLangExperimentalPythonBindings.PygenEffectSynthDefs import Effect, In, Out

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
        return [self[key] for key in self.sort_by("synthdef")]

    def sort_by(self, attr):
        """ Returns the keys sorted by attribute name"""
        return sorted(self.keys(), key=lambda effect: getattr(self[effect], attr))

    def new(self, foxdot_arg_name, synthdef, args, order=2):
        self[foxdot_arg_name] = Effect(
            foxdot_arg_name, synthdef, args, order == 0)

        if order in self.order:

            self.order[order].append(foxdot_arg_name)

        else:

            self.order[order] = [foxdot_arg_name]

        # Store the main keywords together

        self.kw.append(foxdot_arg_name)

        # Store other sub-keys

        for arg in args:
            if arg not in self.all_kw:
                self.all_kw.append(arg)

            # Store the default value

            self.defaults[arg] = args[arg]

        return self[foxdot_arg_name]

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
            effect.load()
        In()
        Out()
        return
