"""Lightweight integration tests for the param_N=value player-variant syntax
(lots 2-5 of ignored_files/plan_player_variants.md).

These exercise Player.assign_instrument/_sync_variant_players end to end,
without booting a real SuperCollider server: Player.main_event_clock and
Player.effect_manager are swapped for minimal fakes, since importing the
full `renardo.runtime` package tries to reach a live audio server and
blocks in this environment.
"""
import pytest

from renardo.lib.Player.player import Player
from renardo.lib.InstrumentProxy import InstrumentProxy
from renardo.lib.Code.main_lib import FoxDotCode
from renardo.sc_backend import SamplePlayer


class FakeSolo:
    def active(self):
        return False


class FakeClock:
    now_flag = False
    solo = FakeSolo()
    playing = []

    def now(self):
        return 0

    def next_bar(self):
        return 0

    def bar_length(self):
        return 4

    def schedule(self, *args, **kwargs):
        pass

    def osc_message_time(self):
        return 0

    def beat_dur(self, x):
        return 0


class FakeEffectManager:
    defaults = {}

    def all_kwargs(self):
        return []

    def kwargs(self):
        return []


@pytest.fixture(autouse=True, scope="module")
def player_test_env():
    Player.set_clock(FakeClock())
    Player.set_effect_manager(FakeEffectManager())
    # A list rather than a dict: SamplePlayer's sentinel object isn't
    # hashable, and `in` on a list falls back to equality instead of hashing.
    Player.set_synth_dict([])
    Player.set_buffer_manager(None)


def make_player(name):
    """Fresh Player, registered in FoxDotCode.namespace like the real
    startup pool does, so _sync_variant_players finds it via `self.id`."""
    player = Player(name)
    FoxDotCode.namespace[name] = player
    return player


def send(player, name, degree, **kwargs):
    player.assign_instrument(InstrumentProxy(name, degree, kwargs))
    return player


def variant(base_name, n):
    return FoxDotCode.namespace.get(f"{base_name}_{n}")


def test_creates_variant_and_leaves_base_untouched():
    b1 = make_player("v1")
    send(b1, "blip", [0, 2, 4, 5], dur=.25, oct=5, oct_2=6)

    b1_2 = variant("v1", 2)
    assert b1_2 is not None
    assert b1_2.oct == 6
    assert b1.oct == 5
    assert b1_2.dur == b1.dur


def test_groups_multiple_params_on_the_same_variant():
    b1 = make_player("v2")
    send(b1, "blip", [0, 2, 4, 5], dur=.25, oct=5, oct_2=6, dur_2=.125)

    b1_2 = variant("v2", 2)
    assert b1_2.oct == 6
    assert b1_2.dur == .125
    assert b1.dur == .25


def test_creates_several_variants_at_once():
    b1 = make_player("v3")
    send(b1, "blip", [0, 2, 4, 5], dur=.25, oct=5, oct_2=6, oct_3=7)

    assert variant("v3", 2).oct == 6
    assert variant("v3", 3).oct == 7


def test_degree_n_overrides_the_note_pattern():
    b1 = make_player("v4")
    send(b1, "blip", [0, 2, 4, 5], dur=.25, oct=5, degree_2=[0, 1, 2, 3])

    # .degree returns a lazily-evaluated PlayerKey (only the current step of
    # the pattern); compare the actual stored pattern in .attr instead.
    b1_2 = variant("v4", 2)
    assert list(b1_2.attr["degree"]) == [0, 1, 2, 3]
    assert list(b1.attr["degree"]) == [0, 2, 4, 5]


def test_explicit_degree_kwarg_does_not_collide_with_positional_degree():
    # degree passed as `degree=...` lands in instrument.kwargs rather than
    # instrument.degree (only the first positional argument does) -- must
    # not be passed twice to update_args_and_start (regression test).
    b1 = make_player("v4b")
    proxy = InstrumentProxy(
        "blip", None,
        {"degree": [0, 2, 4, 5], "dur": .25, "oct": 5, "degree_2": [7, 9, 11, 12]},
    )
    b1.assign_instrument(proxy)

    b1_2 = variant("v4b", 2)
    assert list(b1.attr["degree"]) == [0, 2, 4, 5]
    assert list(b1_2.attr["degree"]) == [7, 9, 11, 12]


def test_live_update_reuses_the_same_variant_instance():
    b1 = make_player("v5")
    send(b1, "blip", [0, 2, 4, 5], dur=.25, oct=5, oct_2=6)
    b1_2_before = variant("v5", 2)

    send(b1, "blip", [0, 2, 4, 5], dur=.25, oct=5, oct_2=8)
    b1_2_after = variant("v5", 2)

    assert b1_2_after is b1_2_before
    assert b1_2_after.oct == 8


def test_removing_suffix_stops_the_variant():
    b1 = make_player("v6")
    send(b1, "blip", [0, 2, 4, 5], dur=.25, oct=5, oct_2=6)
    b1_2 = variant("v6", 2)
    assert b1_2.isplaying is True

    send(b1, "blip", [0, 2, 4, 5], dur=.25, oct=5)
    assert b1_2.isplaying is False
    assert 2 not in b1._variant_children


def test_stop_cascades_to_variants():
    b1 = make_player("v7")
    send(b1, "blip", [0, 2, 4, 5], dur=.25, oct=5, oct_2=6, oct_3=7)
    b1_2, b1_3 = variant("v7", 2), variant("v7", 3)
    assert b1_2.isplaying and b1_3.isplaying

    b1.stop()

    assert b1_2.isplaying is False
    assert b1_3.isplaying is False


def test_chained_methods_are_replayed_on_variants():
    b1 = make_player("v8")
    proxy = InstrumentProxy("blip", [0, 2, 4, 5], {"dur": .25, "oct": 5, "oct_2": 6})
    proxy.methods = [("every", ((4, "reverse"), {}))]
    b1.assign_instrument(proxy)

    # `.every(4, "reverse")` records a repeating call in `repeat_events`,
    # keyed by the method name -- check it landed on both the base player
    # and its variant, not just the base.
    b1_2 = variant("v8", 2)
    assert "reverse" in b1.repeat_events
    assert "reverse" in b1_2.repeat_events


def test_room2_without_underscore_is_not_a_variant_marker():
    b3 = make_player("v9")
    send(b3, "blip", [0, 2, 4, 5], dur=.25, oct=5, room2=.5)

    assert variant("v9", 2) is None
    assert b3.room2 == .5


def test_out_of_range_suffixes_are_ignored():
    b1 = make_player("v10")
    send(b1, "blip", [0, 2, 4, 5], dur=.25, oct=5, oct_1=99, oct_0=99, oct_10=99)

    assert variant("v10", 1) is None
    assert variant("v10", 0) is None
    assert variant("v10", 10) is None


def test_silent_overwrite_stops_the_previous_unrelated_player():
    unrelated = make_player("v11_2")
    send(unrelated, "pluck", [7], dur=1)
    assert unrelated.isplaying is True

    b1 = make_player("v11")
    send(b1, "blip", [0, 2, 4, 5], dur=.25, oct=5, oct_2=6)

    assert unrelated.isplaying is False
    replaced = variant("v11", 2)
    assert replaced.oct == 6


def test_works_for_sample_players_too():
    p1 = make_player("v12")
    send(p1, SamplePlayer, "x-x-", sample=2, room_2=.5)

    p1_2 = variant("v12", 2)
    assert p1_2 is not None
    assert p1_2.room == .5
    assert "room" not in p1.attr  # room_2 must not leak onto the base player
