from typing import Mapping

class MidiMapFactory:
    @classmethod
    def generate_midimap(cls, midi_map):
        if midi_map and isinstance(midi_map, str):
            if midi_map == 'stdrum':
                result = cls.stdrum_midimap()
            if midi_map == 'threesquare':
                result = cls.threesquare_midimap()
            if midi_map == 'linear':
                result = cls.linear_midimap()
        elif midi_map and isinstance(midi_map, Mapping):
            # overwrite default midi_map with provided map
            result = cls.threesquare_midimap() | midi_map
        else:
            result = cls.linear_midimap()
            result = result | {'default': 2, ' ': -200, '.': -200}
        return result

    @classmethod
    def linear_midimap(cls):
        lowcase = list(range(97, 123))
        upcase = list(range(65, 91))
        base_midi_map = {'default': 2, ' ': -200, '.': -200}
        for i in range(52):
            if i % 2 == 0:
                base_midi_map[chr(lowcase[i//2])] = i
            else:
                base_midi_map[chr(upcase[i//2])] = i
        return base_midi_map

    @classmethod
    def threesquare_midimap(cls):
        lowcase = list(range(97, 123))
        upcase = list(range(65, 91))
        base_midi_map = {'default': 2, ' ': -200, '.':-200 }
        for i in range(16):
            base_midi_map[chr(lowcase[i])] = i
        for i in range(16):
            base_midi_map[chr(upcase[i])] = i+16
        for i in range(10):
            k = i + 16
            j = i + 32
            base_midi_map[chr(lowcase[k])] = j
            base_midi_map[chr(upcase[k])] = j+10
        return base_midi_map

    @classmethod
    def stdrum_midimap(cls):
        base_midi_map = {
            'default': 2,
            ' ': -100,
            'x': 0,
            'r': 1,
            'o': 2,
            'c': 3,
            'w': 4,
            'T': 5,
            'H': 6,
            't': 7,
            's': 8,
            'm': 9,
            '=': 10,
            '-': 11,
            'p': 12,
            '*': 13,
            'h': 14,
            'b': 15,
        }
        return base_midi_map