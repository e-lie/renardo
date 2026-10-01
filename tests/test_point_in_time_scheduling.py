"""Regression tests for PointInTime deferred scheduling on the TempoClock.

A clock refactor dropped the ``isinstance(beat, PointInTime)`` branch from
``TempoClock.schedule`` (and the ``to_be_scheduled`` collection), which made

    Clock.schedule(func, pit)
    pit.beat = Clock.now() + 16

blow up with ``TypeError: '<' not supported between instances of
'PointInTime' and 'float'`` inside the scheduling queue.
"""
from renardo.lib.TempoClock.clock import (
    PointInTime,
    PersistentPointInTime,
    TempoClock,
)
from renardo.lib.TempoClock.scheduling_queue import SchedulingQueue


class FakeServer:
    def sendOSC(self, message):
        pass


def make_clock():
    clock = TempoClock.__new__(TempoClock)
    clock.to_be_scheduled = []
    clock.ticking = True
    clock.playing = []
    clock.items = []
    clock.server = FakeServer()
    clock.scheduling_queue = SchedulingQueue(clock=clock)
    return clock


def test_schedule_with_undefined_point_defers_until_defined():
    clock = make_clock()
    calls = []

    def footworking():
        calls.append("ran")

    pit = PointInTime()
    clock.schedule(footworking, pit)

    # Nothing queued yet, but the schedulable is tracked for later.
    assert len(clock.scheduling_queue) == 0
    assert len(clock.to_be_scheduled) == 1

    pit.beat = 16.0

    assert len(clock.scheduling_queue) == 1
    assert clock.scheduling_queue.data[0].beat == 16.0


def test_schedule_with_already_defined_point_queues_immediately():
    clock = make_clock()
    pit = PointInTime(8.0)

    clock.schedule(lambda: None, pit)

    assert len(clock.scheduling_queue) == 1
    assert clock.scheduling_queue.data[0].beat == 8.0


def test_persistent_point_reschedules_on_each_definition():
    clock = make_clock()
    ppit = PersistentPointInTime()

    clock.schedule(lambda: None, ppit)
    ppit.beat = 4.0
    assert len(clock.scheduling_queue) == 1

    ppit.beat = 12.0
    assert len(clock.scheduling_queue) == 2
