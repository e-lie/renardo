


# Name of SamplePlayer and LoopPlayer SynthDef
class _SamplePlayer:
    names = ('play1', 'play2',)

    def __eq__(self, other):
        return other in self.names

    def __ne__(self, other):
        return other not in self.names


class _LoopPlayer:
    names = ("loop", "gsynth", 'stretch')

    def __eq__(self, other):
        return other in self.names

    def __ne__(self, other):
        return other not in self.names


class _MidiPlayer:
    name = "MidiOut"

    def __eq__(self, other):
        return other == self.name

    def __ne__(self, other):
        return other != self.name


SamplePlayer = _SamplePlayer()
LoopPlayer = _LoopPlayer()
MidiPlayer = _MidiPlayer()