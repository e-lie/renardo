import unittest

from renardo_lib.SynthDefManagement.SynthDict import SynthDict


class TestSynthDict(unittest.TestCase):
    def setUp(self) -> None:
        self.SynthDefs = SynthDict()

    def test_repr(self):
        self.SynthDefs['synth1'] = ...
        self.SynthDefs['synth2'] = ...

        self.assertEqual(repr(self.SynthDefs), "['synth1', 'synth2']")
        self.assertEqual(str(self.SynthDefs), "['synth1', 'synth2']")


if __name__ == '__main__':
    unittest.main()
