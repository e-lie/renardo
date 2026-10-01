"""Unit tests for the renardo -> Ableton Live scale/root correspondence.

These don't need a running Live: they only exercise the pure resolution logic
in ``renardo.ableton_backend.scale_sync``.
"""
from renardo.ableton_backend.scale_sync import (
    live_scale_name,
    resolve_scale_and_root,
)
from renardo.lib.Scale import Scale
from renardo.lib.Root import Root
from renardo.lib.TimeVar import TimeVar, Pvar


class FakeMetro:
    ticking = True
    bpm = 120
    time = 0.0

    def now(self):
        return 0.0

    def bar_length(self):
        return 4


def setup_module(module):
    TimeVar.set_clock(FakeMetro())


def teardown_function(function):
    Scale.default = "major"
    Root.default = "C"


def test_live_scale_name_by_explicit_name():
    assert live_scale_name("major", (0, 2, 4, 5, 7, 9, 11)) == "Major"
    assert live_scale_name("minor", (0, 2, 3, 5, 7, 8, 10)) == "Minor"
    assert live_scale_name("aeolian", (0, 2, 3, 5, 7, 8, 10)) == "Minor"
    assert live_scale_name("minorPentatonic", (0, 3, 5, 7, 10)) == "Minor Pentatonic"


def test_live_scale_name_by_interval_fallback():
    # Unknown name, but intervals match a built-in Live scale
    assert live_scale_name("weird", (0, 2, 4, 5, 7, 9, 11)) == "Major"


def test_live_scale_name_unresolvable():
    assert live_scale_name("custom", (0, 2, 3, 5, 6, 9, 10)) is None
    assert live_scale_name(None, (0, 1, 4, 6, 9)) is None


def test_resolve_scale_and_root_static():
    Scale.default = "dorian"
    Root.default = "D"

    name, intervals, root = resolve_scale_and_root()
    assert name == "dorian"
    assert intervals == (0, 2, 3, 5, 7, 9, 10)
    assert root == 2
    assert live_scale_name(name, intervals) == "Dorian"


def test_resolve_scale_and_root_with_timevar_scale():
    Scale.default = Pvar([Scale.major, Scale.minor], 16)
    Root.default = "C"

    # Should not raise; at clock position 0 the Pvar yields Scale.major
    name, intervals, root = resolve_scale_and_root()
    assert root == 0
    assert live_scale_name(name, intervals) == "Major"


def test_resolve_scale_and_root_custom_intervals():
    Scale.default = [0, 1, 4, 6, 9]
    Root.default = "C"

    name, intervals, root = resolve_scale_and_root()
    assert root == 0
    assert live_scale_name(name, intervals) is None
