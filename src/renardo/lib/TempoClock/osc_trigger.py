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

OSC_TRIGGER_PORT = 57430


class _OscTriggerServer:
    """Lazily-started OSC server shared by every OscTrigger instance."""

    def __init__(self):
        self._dispatcher = osc_dispatcher.Dispatcher()
        self._server = None
        self._thread = None

    def register(self, address, handler):
        self._dispatcher.map(address, handler)
        self._ensure_started()

    def _ensure_started(self):
        if self._server is not None:
            return
        self._server = ThreadingOSCUDPServer(("0.0.0.0", OSC_TRIGGER_PORT), self._dispatcher)
        self._thread = threading.Thread(
            target=self._server.serve_forever, daemon=True, name="osc-trigger-server"
        )
        self._thread.start()
        logger.info(f"OSC trigger server listening on port {OSC_TRIGGER_PORT}")


_server = _OscTriggerServer()
_triggers = {}


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
