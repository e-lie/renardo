"""
Global, live-mutable default values for Player parameters.

Mirrors the trick used by Root.default / Scale.default (see Root.py / Scale.py):
".default" is a single mutable object created once. Assigning to it never rebinds
the attribute, it mutates the object's contents in place, so any Player holding a
reference to that object (instead of a copy of its current value) transparently
sees future changes on its next event.

Setting a `.default` to `None` disables it: Player.reset()/update_args_and_start()
(see Player/player.py) fall back to the pre-ParamDefault literal for that attribute
instead of applying a global override for any *new* binding (a fresh player, or a
retrigger in non-sticky mode). Disabling never rewrites `.value` itself to None --
a Player that's already holding a live reference to this cell just keeps observing
its last real value, so it can never end up trying to use `None` as a musical value.
"""


class ParamDefaultValue:
    """A single mutable default value cell (mirrors Root.py's Note trick).

    `enabled` tracks whether this default is active; setting it to `None` via
    `.set(None)` flips `enabled` to False *without* touching `.value`, so any
    Player already holding a reference to this cell keeps reading its last
    real value instead of suddenly seeing None.
    """

    def __init__(self, value):
        self.value = value
        self.enabled = True

    def set(self, value):
        if value is None:
            self.enabled = False
        else:
            self.enabled = True
            self.value = value
        return self

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)

    def __float__(self):
        return float(self.value)

    def __int__(self):
        return int(self.value)


class _SingleDefault:
    """Default holder for a single global default value (Oct, Dur, Sus, Pan, Rate, Sample)."""

    def __init__(self, initial):
        self.default = ParamDefaultValue(initial)

    def __setattr__(self, key, value):
        if key == "default" and key in vars(self):
            self.default.set(value)
        else:
            self.__dict__[key] = value


class _SeedDefault:
    """Global default seed for random pattern generators (PRand, PWhite, etc.).

    Unlike the Player-attribute defaults above, this isn't read per-event through
    a Player -- it wraps RandomGenerator.set_override_seed() (see
    lib/Patterns/Generators.py), which only affects generators *created* from
    this point on (existing generator instances keep whatever randomness they
    already had). Setting `.default = None` clears the override, restoring
    FoxDot's normal unseeded randomness for new generators.
    """

    def __init__(self):
        self.default = None

    def __setattr__(self, key, value):
        if key == "default":
            self.__dict__[key] = value
            from renardo.lib.Patterns.Generators import RandomGenerator
            RandomGenerator.set_override_seed(value)
        else:
            self.__dict__[key] = value


class _PlayerDefaultsSettings:
    """Shared toggle controlling override persistence for the params below."""

    def __init__(self):
        # True  = explicit per-player value persists until reset/kill (current/legacy behavior)
        # False = Root/Scale-style: reverts to the live global default on every bare `>>`
        self.sticky_override = True


Oct = _SingleDefault(5)
Pan = _SingleDefault(0)
# 1 (not 0!) matches the pre-existing default from the "striate" effect
# (renardo/runtime/python_defined_effect_synthdefs.py), which Player.reset()'s
# fx_attributes loop applies to self.rate. For SamplePlayer/LoopPlayer, "rate"
# is also the key parameter server_manager.get_init_node() sends to the
# "startSound" node that triggers buffer playback — 0 silences all sample
# playback outright.
Rate = _SingleDefault(1)
Sample = _SingleDefault(0)

Dur = _SingleDefault(1)
Sus = _SingleDefault(1)

Seed = _SeedDefault()

PlayerDefaults = _PlayerDefaultsSettings()
