"""
OscTrigger
==========

Lets a scheduling macro block (or a plain `Clock.schedule` call) be fired
by an incoming OSC message instead of a beat number:

    # {trig("/myroute")}
    b1 >> blip()

is equivalent to:

    Clock.schedule(_macro_func, beat=trig("/myroute"))

Every OSC message received on "/myroute" causes all callables scheduled
against that trigger to run on the Clock, exactly like a recurring
rendez-vous point. Message arguments are currently ignored.

A single UDP server (python-osc) is shared by every OscTrigger in the
process and is started lazily on first use.
"""

import threading

from pythonosc import dispatcher as osc_dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer

from renardo.logger import get_logger

logger = get_logger('lib.TempoClock.osc_trigger')

DEFAULT_OSC_TRIGGER_ADDR = "127.0.0.1"
DEFAULT_OSC_TRIGGER_PORT = 57430


class _OscTriggerServer:
    """Lazily-started OSC server shared by every OscTrigger instance.

    Bind address/port are configurable via `Clock.osc_trig_addr` /
    `Clock.osc_trig_port`; changing either restarts the server if it was
    already running.
    """

    def __init__(self):
        self._dispatcher = osc_dispatcher.Dispatcher()
        self._server = None
        self._thread = None
        self.addr = DEFAULT_OSC_TRIGGER_ADDR
        self.port = DEFAULT_OSC_TRIGGER_PORT

    def register(self, address, handler):
        self._dispatcher.map(address, handler)
        self._ensure_started()

    def configure(self, addr=None, port=None):
        changed = False
        if addr is not None and addr != self.addr:
            self.addr = addr
            changed = True
        if port is not None and port != self.port:
            self.port = port
            changed = True
        if changed and self._server is not None:
            self._restart()

    def _ensure_started(self):
        if self._server is not None:
            return
        self._start()

    def _start(self):
        self._server = ThreadingOSCUDPServer((self.addr, self.port), self._dispatcher)
        self._thread = threading.Thread(
            target=self._server.serve_forever, daemon=True, name="osc-trigger-server"
        )
        self._thread.start()
        logger.info(f"OSC trigger server listening on {self.addr}:{self.port}")

    def _restart(self):
        if self._server is not None:
            self._server.shutdown()
            self._server = None
            self._thread = None
        self._start()


_server = _OscTriggerServer()
_triggers = {}


def configure(addr=None, port=None):
    """Change the OSC trigger server's bind address/port (restarts it if already running)."""
    _server.configure(addr=addr, port=port)


def get_addr():
    return _server.addr


def get_port():
    return _server.port


class OscTrigger:
    """Fires every callable scheduled against it whenever `address` receives an OSC message."""

    def __init__(self, address):
        self.address = address
        self._schedulables = []
        _server.register(address, self._on_message)

    def add_schedulable(self, schedulable):
        self._schedulables.append(schedulable)

    def _on_message(self, address, *osc_args):
        for schedulable in self._schedulables:
            schedulable.clock.schedule(
                schedulable.callable_obj,
                beat=schedulable.clock.now(),
                args=schedulable.args,
                kwargs=schedulable.kwargs,
                is_priority=schedulable.is_priority,
            )

    def __repr__(self):
        return f"OscTrigger({self.address!r}, {len(self._schedulables)} listeners)"


def trig(address):
    """Return the OscTrigger for `address`, creating and registering it on first use."""
    if address not in _triggers:
        _triggers[address] = OscTrigger(address)
    return _triggers[address]
