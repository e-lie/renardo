class SynthDict(dict):
    def __repr__(self):
        return str(list(self.keys()))


SynthDefs = SynthDict()
