"""
ReaperFreshInstrumentFacade + create_reaper_instruments()
API haut niveau identique à ableton_backend.
"""

from typing import Any, Dict, Optional

from renardo.lib.Patterns import Pattern
from renardo.reaper_backend_fresh.reaper_fresh_project import ReaperFreshProject, _snake
from renardo.reaper_backend_fresh.reaper_fresh_instrument import ReaperFreshInstrument


class ReaperFreshInstrumentWrapper:
    """Wrapper retourné par .out — se comporte comme un SynthDef pour le Player."""

    def __init__(self, facade: "ReaperFreshInstrumentFacade"):
        self._facade = facade
        self.name = f"ReaperFresh_{facade._snake_name}"

    def __call__(self, degree=0, **kwargs):
        return self._facade.create_instrument(degree=degree, **kwargs)


class ReaperFreshInstrumentFacade:
    """
    Façade liée à une track REAPER.
    Usage :
        kick = ReaperFreshInstrumentFacade(project, "Kick", midi_channel=1)
        p1 >> kick.out(degree=0, dur=0.5)
    """

    def __init__(self, project: ReaperFreshProject, track_name: str,
                 midi_channel: int = 1, midi_off: bool = False,
                 sus=None):
        self._project = project
        self.track_name = track_name
        self._snake_name = _snake(track_name)
        self._midi_channel = midi_channel
        self._midi_off = midi_off
        self._default_sus = sus

        track_info = project._track_map.get(self._snake_name)
        if track_info is None:
            raise ValueError(f"Track '{track_name}' not found in REAPER project. "
                             f"Available: {list(project._track_map.keys())}")

        project.register_instrument(track_name, self)

    @property
    def out(self) -> ReaperFreshInstrumentWrapper:
        return ReaperFreshInstrumentWrapper(self)

    def create_instrument(self, degree=0, sus=None, **kwargs) -> ReaperFreshInstrument:
        if sus is None:
            sus = self._default_sus
        if sus is None:
            dur = kwargs.get("dur", 1)
            sus = Pattern(dur) - 0.03
        else:
            sus = Pattern(sus)

        # Expand shorthand keys to full track-prefixed keys when resolvable
        processed = {}
        for key, value in kwargs.items():
            full = f"{self._snake_name}_{key}"
            if self._project._resolve_param(full, self._snake_name):
                processed[full] = value
            else:
                processed[key] = value

        return ReaperFreshInstrument(
            project=self._project,
            track_name=self._snake_name,
            channel=self._midi_channel - 1,
            degree=degree,
            midi_off=self._midi_off,
            sus=sus,
            **processed,
        )

    def __repr__(self):
        return (f"ReaperFreshInstrumentFacade("
                f"track='{self.track_name}', channel={self._midi_channel})")


def create_reaper_instruments(max_midi_tracks: int = 16,
                              scan_audio_tracks: bool = True) -> Dict[str, Any]:
    """
    Scanne le projet REAPER courant et crée une facade par track.

    Returns:
        dict {track_snake_name: ReaperFreshInstrumentFacade, '_project': ReaperFreshProject}
    """
    from renardo import runtime

    project = ReaperFreshProject(scan=True)
    runtime.reaper_fresh_project = project

    instruments: Dict[str, Any] = {}
    midi_channel_counter = 0

    for snake_name, track_info in project._track_map.items():
        is_midi = track_info["is_midi"]

        if is_midi and midi_channel_counter >= max_midi_tracks:
            continue
        if not is_midi and not scan_audio_tracks:
            continue

        if is_midi:
            midi_channel_counter += 1
            channel = midi_channel_counter
            midi_off = False
        else:
            channel = 1
            midi_off = True

        facade = ReaperFreshInstrumentFacade(
            project=project,
            track_name=snake_name,
            midi_channel=channel,
            midi_off=midi_off,
        )
        instruments[snake_name] = facade

    instruments["_project"] = project
    return instruments
