"""
Global, live-mutable default values for Player parameters.

Mirrors the trick used by Root.default / Scale.default (see Root.py / Scale.py):
".default" is a single mutable object created once. Assigning to it never rebinds
the attribute, it mutates the object's contents in place, so any Player holding a
reference to that object (instead of a copy of its current value) transparently
sees future changes on its next event.
"""


class ParamDefaultValue:
    """A single mutable default value cell (mirrors Root.py's Note trick)."""

    def __init__(self, value):
        self.value = value

    def set(self, value):
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
    """Default holder for params with a single default value (Oct, Pan, Rate, Sample)."""

    def __init__(self, initial):
        self.default = ParamDefaultValue(initial)

    def __setattr__(self, key, value):
        if key == "default" and key in vars(self):
            self.default.set(value)
        else:
            self.__dict__[key] = value


class _SplitDefault:
    """Default holder for params with a synth/sampler split (Dur, Sus).

    `link_sampler_default`, when True, makes `sampler_default` mirror `default`
    for users who don't want the sample/synth distinction.
    """

    def __init__(self, default_value, sampler_value):
        self.default = ParamDefaultValue(default_value)
        self.sampler_default = ParamDefaultValue(sampler_value)
        self.link_sampler_default = False

    def __setattr__(self, key, value):
        if key == "default" and key in vars(self):
            self.default.set(value)
            if self.__dict__.get("link_sampler_default"):
                self.sampler_default.set(value)
        elif key == "sampler_default" and key in vars(self):
            self.sampler_default.set(value)
        elif key == "link_sampler_default":
            self.__dict__[key] = value
            if value:
                self.sampler_default.set(self.default.value)
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

Dur = _SplitDefault(1, 0.5)
Sus = _SplitDefault(1, 0.5)

PlayerDefaults = _PlayerDefaultsSettings()
