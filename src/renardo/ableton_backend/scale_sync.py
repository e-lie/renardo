"""
Scale/root correspondence between renardo and Ableton Live 12 "Scale Awareness".

renardo is the source of truth. This module only *reads* renardo's current
tonality (``Scale.default`` / ``Root.default``, TimeVars included) and maps it to
the vocabulary understood by AbletonOSC (``/live/song/set/root_note`` int 0-11,
``/live/song/set/scale_name`` string).

No OSC is sent from here - see ``AbletonProject`` for the polling thread that
pushes the resolved values.
"""

# Built-in scales of Live 12: display name -> tuple of semitone intervals.
LIVE_SCALE_INTERVALS = {
    "Major": (0, 2, 4, 5, 7, 9, 11),
    "Minor": (0, 2, 3, 5, 7, 8, 10),
    "Dorian": (0, 2, 3, 5, 7, 9, 10),
    "Mixolydian": (0, 2, 4, 5, 7, 9, 10),
    "Lydian": (0, 2, 4, 6, 7, 9, 11),
    "Phrygian": (0, 1, 3, 5, 7, 8, 10),
    "Locrian": (0, 1, 3, 5, 6, 8, 10),
    "Whole Tone": (0, 2, 4, 6, 8, 10),
    "Half-whole Dim.": (0, 1, 3, 4, 6, 7, 9, 10),
    "Whole-half Dim.": (0, 2, 3, 5, 6, 8, 9, 11),
    "Minor Blues": (0, 3, 5, 6, 7, 10),
    "Minor Pentatonic": (0, 3, 5, 7, 10),
    "Major Pentatonic": (0, 2, 4, 7, 9),
    "Harmonic Minor": (0, 2, 3, 5, 7, 8, 11),
    "Harmonic Major": (0, 2, 4, 5, 7, 8, 11),
    "Melodic Minor": (0, 2, 3, 5, 7, 9, 11),
    "Hungarian Minor": (0, 2, 3, 6, 7, 8, 11),
    "Lydian Augmented": (0, 2, 4, 6, 8, 9, 11),
    "Lydian Dominant": (0, 2, 4, 6, 7, 9, 10),
    "Super Locrian": (0, 1, 3, 4, 6, 8, 10),
}

# Direct map of renardo ``ScalePattern.name`` -> Live scale display name.
# Covers cases where names differ or where several renardo scales share
# intervals (so the interval fallback would be ambiguous).
RENARDO_NAME_TO_LIVE = {
    "major": "Major",
    "justMajor": "Major",
    "minor": "Minor",
    "aeolian": "Minor",
    "justMinor": "Minor",
    "dorian": "Dorian",
    "mixolydian": "Mixolydian",
    "lydian": "Lydian",
    "phrygian": "Phrygian",
    "locrian": "Locrian",
    "wholeTone": "Whole Tone",
    "diminished": "Half-whole Dim.",
    "halfWhole": "Half-whole Dim.",
    "wholeHalf": "Whole-half Dim.",
    "blues": "Minor Blues",
    "minorPentatonic": "Minor Pentatonic",
    "majorPentatonic": "Major Pentatonic",
    "harmonicMinor": "Harmonic Minor",
    "harmonicMajor": "Harmonic Major",
    "melodicMinor": "Melodic Minor",
    "hungarianMinor": "Hungarian Minor",
    "lydianAug": "Lydian Augmented",
    "lydianDom": "Lydian Dominant",
    "altered": "Super Locrian",
}

# Reverse lookup: normalised intervals -> Live scale name.
_INTERVALS_TO_LIVE = {v: k for k, v in LIVE_SCALE_INTERVALS.items()}


def live_scale_name(name, intervals):
    """
    Best-effort resolution of a renardo scale to a Live scale name.

    Tries the explicit name map first, then an exact interval match.
    Returns ``None`` when no built-in Live scale matches (caller should then
    leave Live's scale untouched).
    """
    if name is not None:
        mapped = RENARDO_NAME_TO_LIVE.get(name)
        if mapped is not None:
            return mapped

    if intervals is not None:
        return _INTERVALS_TO_LIVE.get(tuple(intervals))

    return None


def resolve_scale_and_root():
    """
    Read renardo's current tonality.

    Returns a ``(name, intervals, root)`` tuple where:
      - ``name`` is the current ``ScalePattern.name`` or ``None``
      - ``intervals`` is a tuple of ints (semitone offsets) or ``None``
      - ``root`` is an int in 0-11 or ``None``

    TimeVars (``Pvar`` / ``var`` / ``TimeVar``) are resolved to their value at
    the current clock position. Never raises.
    """
    name = None
    intervals = None
    root = None

    try:
        from renardo.lib.Scale import Scale

        s = Scale.default
        data = getattr(s, "data", None)
        cur = data.now() if hasattr(data, "now") else s
        name = getattr(cur, "name", None)
        try:
            intervals = tuple(int(x) for x in list(cur))
        except (TypeError, ValueError):
            intervals = None
    except Exception:
        pass

    try:
        from renardo.lib.Root import Root

        rn = Root.default.num
        rn = rn.now() if hasattr(rn, "now") else rn
        root = int(rn) % 12
    except Exception:
        pass

    return name, intervals, root
