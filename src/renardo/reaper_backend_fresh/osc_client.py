"""OSC client for communicating with the Rust REAPER fresh extension."""

import struct
import threading
from typing import Optional
from pythonosc import udp_client, osc_server, dispatcher

from renardo.logger import get_logger

logger = get_logger("reaper_fresh.osc_client")


class ReaperFreshOscClient:
    """UDP OSC client talking to the Rust fresh extension on ports 9877/9878."""

    def __init__(self, host: str = "127.0.0.1", send_port: int = 9877,
                 receive_port: int = 9878, timeout: float = 2.0):
        self.host = host
        self.send_port = send_port
        self.receive_port = receive_port
        self.timeout = timeout

        self._client = udp_client.SimpleUDPClient(host, send_port)
        self._responses: dict = {}
        self._events: dict = {}

        self._dispatcher = dispatcher.Dispatcher()
        self._dispatcher.set_default_handler(self._on_response)

        self._server = osc_server.ThreadingOSCUDPServer(
            (host, receive_port), self._dispatcher
        )
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

        logger.info(f"ReaperFreshOscClient ready — send={send_port} recv={receive_port}")

    def _on_response(self, address: str, *args):
        self._responses[address] = args
        if address in self._events:
            self._events[address].set()

    def send(self, address: str, *args) -> None:
        self._client.send_message(address, list(args) if args else [])

    def request(self, address: str, response_address: str, *args,
                timeout: Optional[float] = None) -> Optional[tuple]:
        t = timeout or self.timeout
        self._responses.pop(response_address, None)
        event = threading.Event()
        self._events[response_address] = event
        try:
            self.send(address, *args)
            if event.wait(t):
                return self._responses.get(response_address)
            logger.warning(f"Timeout waiting for {response_address}")
            return None
        finally:
            self._events.pop(response_address, None)

    # ── project ──────────────────────────────────────────────────────────────

    def get_track_count(self) -> int:
        resp = self.request("/project/track_count", "/project/track_count/response")
        return resp[0] if resp else 0

    def get_tempo(self) -> float:
        resp = self.request("/project/tempo/get", "/project/tempo/get/response")
        return float(resp[0]) if resp else 120.0

    def set_tempo(self, bpm: float) -> None:
        self.send("/project/tempo/set", float(bpm))

    # ── track ─────────────────────────────────────────────────────────────────

    def scan_track(self, track_idx: int, timeout: float = 10.0) -> Optional[dict]:
        resp = self.request("/track/scan", "/track/scan/response",
                            track_idx, timeout=timeout)
        if not resp or resp[0] != "success":
            return None

        data = {
            "index":     resp[1],
            "name":      resp[2] if len(resp) > 2 else "",
            "volume":    resp[3] if len(resp) > 3 else 1.0,
            "pan":       resp[4] if len(resp) > 4 else 0.0,
            "mute":      resp[5] if len(resp) > 5 else False,
            "solo":      resp[6] if len(resp) > 6 else False,
            "rec_arm":   resp[7] if len(resp) > 7 else False,
            "rec_input": resp[8] if len(resp) > 8 else -1,
        }

        if len(resp) > 12 and isinstance(resp[12], bytes):
            data["fx"] = _parse_blob(resp[12])
        else:
            data["fx"] = []

        return data

    def set_track_volume(self, track_idx: int, value: float) -> None:
        self.send("/track/volume/set", track_idx, float(value))

    def set_track_pan(self, track_idx: int, value: float) -> None:
        self.send("/track/pan/set", track_idx, float(value))

    # ── FX ───────────────────────────────────────────────────────────────────

    def set_fx_param(self, track_idx: int, fx_idx: int, param_idx: int,
                     value: float) -> None:
        self.send("/fx/param/set", track_idx, fx_idx, param_idx, float(value))

    def scan_fx_params(self, track_idx: int, fx_idx: int, offset: int = 0,
                       count: int = 50, timeout: float = 5.0) -> Optional[dict]:
        """Fetch a batch of FX parameter metadata.

        Returns:
            {'total': int, 'params': flat_list} where flat_list contains groups of
            [name, value, min, max, formatted] per parameter, or None on failure.
        """
        resp = self.request("/fx/params/scan", "/fx/params/scan/response",
                            track_idx, fx_idx, offset, count, timeout=timeout)
        if not resp or resp[0] != "success":
            return None
        # resp: ["success", track_idx, fx_idx, offset, total_count, blob]
        total = resp[4] if len(resp) > 4 else 0
        blob = resp[5] if len(resp) > 5 and isinstance(resp[5], bytes) else b""
        return {"total": int(total), "params": _parse_blob(blob)}

    # ── MIDI ─────────────────────────────────────────────────────────────────

    def play_note(self, channel: int, note: int, velocity: int,
                  duration_ms: int) -> None:
        logger.debug(f"[REAPER-FRESH OSC] play_note → /note ch={channel} note={note} vel={velocity} dur={duration_ms}ms")
        print(f"[REAPER-FRESH OSC] play_note → /note ch={channel} note={note} vel={velocity} dur={duration_ms}ms")
        self.send("/note", channel, note, velocity, duration_ms)

    def close(self):
        self._server.shutdown()


def _parse_blob(blob: bytes) -> list:
    """Parse the custom binary blob produced by serialize_osc_array() in Rust."""
    items = []
    pos = 0
    if len(blob) < 4:
        return items
    count = int.from_bytes(blob[pos:pos + 4], 'big')
    pos += 4
    for _ in range(count):
        if pos >= len(blob):
            break
        t = chr(blob[pos])
        pos += 1
        if t == 'i' and pos + 4 <= len(blob):
            items.append(int.from_bytes(blob[pos:pos + 4], 'big', signed=True))
            pos += 4
        elif t == 'f' and pos + 4 <= len(blob):
            items.append(struct.unpack('>f', blob[pos:pos + 4])[0])
            pos += 4
        elif t == 's' and pos + 4 <= len(blob):
            length = int.from_bytes(blob[pos:pos + 4], 'big')
            pos += 4
            if pos + length <= len(blob):
                items.append(blob[pos:pos + length].decode('utf-8', errors='ignore'))
                pos += length
        elif t == 'b' and pos + 1 <= len(blob):
            items.append(blob[pos] != 0)
            pos += 1
        elif t == 'n':
            items.append(None)
    return items


# ── singleton ──────────────────────────────────────────────────────────────

_client: Optional[ReaperFreshOscClient] = None


def get_osc_client() -> ReaperFreshOscClient:
    global _client
    if _client is None:
        _client = ReaperFreshOscClient()
    return _client
