import re

# A kwarg named "<name>_N" (N a single digit from 2 to 9) overrides <name>
# for an automatically-generated variant player. Anything outside that
# range (_0, _1, _10, ...) is left untouched as a literal kwarg name -- 1
# is reserved for the base player itself, and multi-digit suffixes are not
# supported (keeps the convention unambiguous, see ignored_files/plan_player_variants.md).
VARIANT_KWARG_RE = re.compile(r"^(.+)_([2-9])$")


def split_variant_kwargs(degree, kwargs):
    """Split the kwargs of a `player >> instrument(...)` call into the base
    player's own values and any per-variant overrides.

    Several kwargs sharing the same variant number are grouped together
    (e.g. `oct_2=6, dur_2=.125` both apply to variant 2). `degree_N`
    overrides the positional degree/note pattern for that variant rather
    than becoming a regular kwarg.

    Returns `(base_degree, base_kwargs, variants)` where `variants` maps
    variant number -> `(variant_degree_override_or_None, overrides_dict)`.
    `variants` is empty when no kwarg matches the variant convention.
    """
    variant_overrides = {}
    base_kwargs = {}

    for key, value in kwargs.items():
        match = VARIANT_KWARG_RE.match(key)
        if match is None:
            base_kwargs[key] = value
            continue
        base_name, digit = match.group(1), int(match.group(2))
        variant_overrides.setdefault(digit, {})[base_name] = value

    if not variant_overrides:
        return degree, kwargs, {}

    variants = {}
    for n, overrides in variant_overrides.items():
        variant_degree = overrides.pop("degree", None)
        variants[n] = (variant_degree, overrides)

    return degree, base_kwargs, variants
