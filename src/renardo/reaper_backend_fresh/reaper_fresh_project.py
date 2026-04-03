"""
ReaperFreshProject — scanne un projet REAPER existant et expose le contrôle
de ses tracks/paramètres/tempo via OSC (extension Rust uniquement).
"""

import re
import threading
import time
from typing import Optional, Any

from renardo.lib.TimeVar import TimeVar
from renardo.logger import get_logger
from renardo.reaper_backend_fresh.osc_client import get_osc_client

logger = get_logger("reaper_fresh.project")


def _snake(name: str) -> str:
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", "_", name)
    return name.lower()


def _parse_fx_blob(flat: list) -> list:
    """
    Transforme la liste plate retournée par le blob de scan en une liste de dicts FX.

    Format blob (séquence répétée par FX) :
      str  fx_name
      bool fx_enabled
      str  fx_preset
      int  param_count
      puis param_count fois : str param_name, float value, float min, float max, str formatted
    """
    fx_list = []
    pos = 0
    n = len(flat)

    while pos < n:
        # Besoin d'au moins : name, enabled, preset, param_count
        if pos + 4 > n:
            break

        fx_name   = flat[pos];     pos += 1
        fx_enabled = flat[pos];    pos += 1
        fx_preset  = flat[pos];    pos += 1
        param_count = flat[pos];   pos += 1

        if not isinstance(param_count, int):
            break

        params = {}
        for _ in range(param_count):
            if pos + 5 > n:
                break
            p_name     = flat[pos]; pos += 1
            p_value    = flat[pos]; pos += 1
            p_min      = flat[pos]; pos += 1
            p_max      = flat[pos]; pos += 1
            p_formatted = flat[pos]; pos += 1

            snake_name = _snake(str(p_name))
            params[snake_name] = {
                "name":      p_name,
                "value":     p_value,
                "min":       p_min,
                "max":       p_max,
                "formatted": p_formatted,
            }

        fx_list.append({
            "name":    fx_name,
            "snake":   _snake(str(fx_name)),
            "enabled": fx_enabled,
            "preset":  fx_preset,
            "params":  params,
        })

    return fx_list


class ReaperFreshProject:
    """
    Wrapper autour du projet REAPER courant.
    Scanne les tracks/FX existants et permet de contrôler paramètres et tempo.
    """

    def __init__(self, scan: bool = True):
        self._osc = get_osc_client()
        self._track_map: dict = {}      # snake_name → track info
        self._param_map: dict = {}      # full_snake_key → param descriptor
        self._instruments: dict = {}

        self._timevar_params: dict = {}  # key → (TimeVar, descriptor)
        self._timevar_bpm: Optional[TimeVar] = None
        self._timevar_lock = threading.Lock()
        self._timevar_running = False
        self._timevar_thread: Optional[threading.Thread] = None

        if scan:
            self.scan()

        self._start_timevar_thread()

    # ── scan ─────────────────────────────────────────────────────────────────

    def scan(self):
        """Scanne le projet REAPER courant et reconstruit les maps."""
        self._track_map.clear()
        self._param_map.clear()

        count = self._osc.get_track_count()
        logger.info(f"Scanning {count} tracks")

        for idx in range(count):
            raw = self._osc.scan_track(idx)
            if raw is None:
                logger.warning(f"scan_track({idx}) returned None")
                continue

            name = raw.get("name", f"track_{idx}")
            snake_name = _snake(name)

            # Déduire si MIDI : rec_input >= 4096 indique une entrée MIDI
            rec_input = raw.get("rec_input", -1)
            is_midi = isinstance(rec_input, int) and rec_input >= 4096

            fx_list = _parse_fx_blob(raw.get("fx", []))

            track_info = {
                "index":   idx,
                "name":    name,
                "is_midi": is_midi,
                "volume":  raw.get("volume", 1.0),
                "pan":     raw.get("pan", 0.0),
                "devices": {},
            }

            # Construire le param_map pour volume/pan de la track
            vol_key = f"{snake_name}_volume"
            pan_key = f"{snake_name}_pan"
            self._param_map[vol_key] = {
                "type":      "volume",
                "track_idx": idx,
                "min":       0.0,
                "max":       4.0,   # REAPER D_VOL : 1.0 = 0dB, 4.0 ≈ +12dB
            }
            self._param_map[pan_key] = {
                "type":      "pan",
                "track_idx": idx,
                "min":       -1.0,
                "max":       1.0,
            }

            for fx in fx_list:
                fx_snake = fx["snake"]
                track_info["devices"][fx_snake] = {
                    "fx_index": fx_list.index(fx),
                    "name":     fx["name"],
                    "params":   fx["params"],
                }

                for p_snake, p_info in fx["params"].items():
                    full_key = f"{snake_name}_{fx_snake}_{p_snake}"
                    self._param_map[full_key] = {
                        "type":      "fx",
                        "track_idx": idx,
                        "fx_idx":    fx_list.index(fx),
                        "param_idx": list(fx["params"].keys()).index(p_snake),
                        "min":       p_info["min"],
                        "max":       p_info["max"],
                    }

            self._track_map[snake_name] = track_info

        logger.info(f"Scan done: {len(self._track_map)} tracks, {len(self._param_map)} params")

    # ── param resolution ─────────────────────────────────────────────────────

    def _resolve_param(self, name: str, track_name: Optional[str] = None) -> Optional[dict]:
        """Résoud un nom de paramètre en descriptor (full key, avec préfixes optionnels)."""
        # Lookup direct
        if name in self._param_map:
            return self._param_map[name]

        if track_name:
            t = _snake(track_name)

            # Avec préfixe track
            candidate = f"{t}_{name}"
            if candidate in self._param_map:
                return self._param_map[candidate]

            # Recherche partielle : toute clé du track qui se termine par _{name}
            suffix = f"_{name}"
            for key, desc in self._param_map.items():
                if key.startswith(t + "_") and key.endswith(suffix):
                    return desc

            # Shortcut : premier device, premier param correspondant
            track_info = self._track_map.get(t)
            if track_info:
                for dev_snake, dev_info in track_info["devices"].items():
                    full = f"{t}_{dev_snake}_{name}"
                    if full in self._param_map:
                        return self._param_map[full]

        return None

    # ── set_parameter ─────────────────────────────────────────────────────────

    def set_parameter(self, name: str, value, track_name: Optional[str] = None) -> bool:
        desc = self._resolve_param(name, track_name)
        if desc is None:
            logger.warning(f"Parameter not found: {name}")
            return False

        if isinstance(value, TimeVar):
            with self._timevar_lock:
                self._timevar_params[name] = (value, desc)
            value = float(value.now())
            self._apply_param(desc, value)
            return True

        with self._timevar_lock:
            self._timevar_params.pop(name, None)

        self._apply_param(desc, float(value))
        return True

    def _apply_param(self, desc: dict, value: float):
        t = desc["type"]
        if t == "volume":
            # value vient de l'utilisateur normalisé [0,1] → D_VOL range [0, 4]
            vol = desc["min"] + value * (desc["max"] - desc["min"])
            self._osc.set_track_volume(desc["track_idx"], vol)
        elif t == "pan":
            pan = desc["min"] + value * (desc["max"] - desc["min"])
            self._osc.set_track_pan(desc["track_idx"], pan)
        elif t == "fx":
            # value déjà normalisée [0,1] — TrackFX_SetParamNormalized attend [0,1]
            v = max(0.0, min(1.0, value))
            self._osc.set_fx_param(desc["track_idx"], desc["fx_idx"], desc["param_idx"], v)

    # ── tempo ─────────────────────────────────────────────────────────────────

    def change_bpm(self, bpm):
        if isinstance(bpm, TimeVar):
            with self._timevar_lock:
                self._timevar_bpm = bpm
            self._osc.set_tempo(float(bpm.now()))
        else:
            with self._timevar_lock:
                self._timevar_bpm = None
            self._osc.set_tempo(float(bpm))

    def get_bpm(self) -> float:
        return self._osc.get_tempo()

    # ── MIDI notes directes ───────────────────────────────────────────────────

    def play_note(self, channel: int, note: int, velocity: int = 100,
                  duration_ms: int = 500):
        self._osc.play_note(channel, note, velocity, duration_ms)

    # ── TimeVar thread ────────────────────────────────────────────────────────

    def _start_timevar_thread(self):
        self._timevar_running = True
        self._timevar_thread = threading.Thread(
            target=self._timevar_loop, daemon=True
        )
        self._timevar_thread.start()

    def _stop_timevar_thread(self):
        self._timevar_running = False
        if self._timevar_thread:
            self._timevar_thread.join(timeout=1.0)

    def _timevar_loop(self):
        interval = 1.0 / 300.0  # 300 Hz
        while self._timevar_running:
            t0 = time.time()

            with self._timevar_lock:
                bpm_tv = self._timevar_bpm
                params_snapshot = list(self._timevar_params.items())

            if bpm_tv is not None:
                try:
                    self._osc.set_tempo(float(bpm_tv.now()))
                except Exception:
                    pass

            for key, (tv, desc) in params_snapshot:
                try:
                    self._apply_param(desc, float(tv.now()))
                except Exception:
                    pass

            elapsed = time.time() - t0
            sleep = interval - elapsed
            if sleep > 0:
                time.sleep(sleep)

    # ── helpers ───────────────────────────────────────────────────────────────

    def get_tracks(self) -> list:
        return list(self._track_map.keys())

    def get_midi_tracks(self) -> list:
        return [k for k, v in self._track_map.items() if v["is_midi"]]

    def get_track_parameters(self, track_name: str) -> dict:
        t = _snake(track_name)
        return {k: v for k, v in self._param_map.items() if k.startswith(t + "_")}

    def register_instrument(self, track_name: str, instrument):
        self._instruments[_snake(track_name)] = instrument

    def get_instrument(self, track_name: str):
        return self._instruments.get(_snake(track_name))

    def print_parameter_map(self):
        print("=== ReaperFresh Parameter Map ===")
        for track_name, info in self._track_map.items():
            kind = "MIDI" if info["is_midi"] else "AUDIO"
            print(f"\nTrack: {track_name} [{kind}] (idx={info['index']})")
            for dev, dev_info in info["devices"].items():
                print(f"  FX [{dev_info['fx_index']}]: {dev_info['name']}")
                for p_snake, p_info in dev_info["params"].items():
                    print(f"    {p_snake}: val={p_info['value']:.3f} "
                          f"[{p_info['min']:.2f}, {p_info['max']:.2f}]")

    def __del__(self):
        self._stop_timevar_thread()
