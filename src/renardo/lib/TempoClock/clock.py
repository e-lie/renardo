from __future__ import absolute_import, division, print_function

import time
from traceback import format_exc as error_stack

import sys
import threading

from .scheduling_queue import SchedulingQueue, SoloPlayer, History, ScheduleError, Wrapper

from renardo.lib.Player import Player
from renardo.lib.TimeVar import TimeVar
from renardo.lib.Midi import MidiIn, MIDIDeviceNotFound
from renardo.sc_backend import TempoClient, ServerManager
from renardo.settings_manager import settings


class TempoClock(object):
    tempo_server = None
    tempo_client = None
    waiting_for_sync = False

    def __init__(self, bpm=120.0, meter=(4, 4)):

        # Flag this when done init
        self.__setup = False

        # debug information

        self.largest_sleep_time = 0
        self.last_block_dur = 0.0

        self.beat = float(0)  # Beats elapsed
        self.last_now_call = float(0)
        self.ticking = True

        # Player Objects stored here
        self.playing = []

        # Store history of osc messages and functions in here
        self.history = History()

        # All other scheduled items go here
        self.items = []

        # General set up
        self.bpm = bpm
        self.meter = meter

        # Create the queue
        self.scheduling_queue = SchedulingQueue(clock=self)
        self.current_block = None

        # Flag for next_bar wrapper
        self.now_flag = False

        # Can be configured
        # self.latency_values = [0.25, 0.5, 0.75]
        self.latency = 0.25  # Time between starting processing osc messages and sending to server
        self.nudge = 0.0  # If you want to synchronise with something external, adjust the nudge
        self.hard_nudge = 0.0

        self.bpm_start_time = time.time()
        self.bpm_start_beat = 0

        # This can be set lower to use less CPU power
        self.sleep_time_between_updates = 0.0001

        self.midi_nudge = 0

        # Debug
        self.debugging = False
        self.__setup = True

        # If one object is going to be played
        self.solo = SoloPlayer()
        self.thread = threading.Thread(target=self.main_loop)

    def start(self):
        """ Starts the clock thread """
        self.thread.daemon = True
        self.thread.start()
        return

    def __str__(self):
        return str(self.scheduling_queue)

    # def __iter__(self):
    #     for x in self.scheduling_queue:
    #         yield x
    #
    # def __len__(self):
    #     return len(self.scheduling_queue)

    def __contains__(self, item):
        return item in self.items


    def reset(self):
        """ Deprecated """
        self.time = self.dtype(0)
        self.beat = self.dtype(0)
        self.start_time = time.time()
        return

    @classmethod
    def set_server(cls, server):
        """ Sets the destination for OSC messages being compiled (the server is also the class
            that compiles them) via objects in the clock. Should be an instance of ServerManager -
            see ServerManager.py for more. """
        assert isinstance(server, ServerManager)
        cls.server = server
        return

    def schedule(self, obj, beat=None, args=(), kwargs={}, is_priority=False):
        """ TempoClock.schedule(callable, beat=None)
            Add a player / event to the queue """
        # Make sure the object can actually be called
        try:
            assert callable(obj)
        except AssertionError:
            raise ScheduleError(obj)

        # Start the clock ticking if not already
        if self.ticking == False:
            self.start()

        # Default is next bar
        if beat is None:
            beat = self.next_bar()

        # Keep track of objects in the Clock
        if obj not in self.playing and isinstance(obj, Player):
            self.playing.append(obj)

        if obj not in self.items:
            self.items.append(obj)

        # Add to the queue
        self.scheduling_queue.add(obj, beat, args, kwargs, is_priority)
        # block.time = self.osc_message_accum

        return None



    def _now(self):
        """ If the bpm is an int or float, use time since the last bpm change to calculate what the current beat is.
            If the bpm is a TimeVar, increase the beat counter by time since last call to _now()"""
        if isinstance(self.bpm, (int, float)):
            self.beat = self.bpm_start_beat + self.get_elapsed_beats_from_last_bpm_change()
        else:
            now = self.get_time()
            self.beat += (now - self.last_now_call) * (self.get_bpm() / 60)
            self.last_now_call = now
        return self.beat

    def now(self):
        """ Returns the total elapsed time (in beats as opposed to seconds) """
        if self.ticking is False:  # Get the time w/o latency if not ticking
            self.beat = self._now()
        return float(self.beat)

    def main_loop(self):
        """ Main event loop that runs in a thread """
        self.ticking = True
        self.polled = False

        while self.ticking:
            beat = self._now()  # get current time
            if self.scheduling_queue.after_next_event(beat):
                self.current_block = self.scheduling_queue.pop()

                # Do the work in a thread
                if len(self.current_block):
                    threading.Thread(
                        target=self._execute_queue_block,
                        args=(self.current_block, beat)
                    ).start()

            if self.sleep_time_between_updates > 0:
                time.sleep(self.sleep_time_between_updates)

        return None

    def _execute_queue_block(self, block, beat):
        """ Private method for calling all the items in the queue block.
            This means the clock can still 'tick' while a large number of
            events are activated  """

        # Set the time to "activate" messages on - adjust in case the block is activated late
        # `beat` is the actual beat this is happening, `block.beat` is the desired time. Adjust
        # the osc_message_time accordingly if this is being called late
        block.time = self.osc_message_time() - self.beat_dur(float(beat) - block.beat)
        for item in block:
            # The item might get called by another item in the queue block
            output = None
            if item.called is False:
                try:
                    output = item.__call__()
                except SystemExit:
                    sys.exit()
                except:
                    print(error_stack())
                # TODO: Get OSC message from the call, and add to list?

        # Send all the message to supercollider together
        block.send_osc_messages()
        # Store the osc messages -- future idea
        # self.history.add(block.beat, block.osc_messages)

        return None

    # @classmethod
    # def add_method(cls, func):
    #     setattr(cls, func.__name__, func)


    # def update_tempo_now(self, bpm):
    #     """ emergency override for updating tempo"""
    #     self.last_now_call = self.bpm_start_time = time.time()
    #     self.bpm_start_beat = self.now()
    #     object.__setattr__(self, "bpm", self._convert_json_bpm(bpm))
    #     # self.update_network_tempo(bpm, start_beat, start_time) -- updates at the bar...
    #     return

    # def set_tempo(self, bpm, override=False):
    #     """ Short-hand for update_tempo and update_tempo_now """
    #     return self.update_tempo_now(bpm) if override else self.update_tempo(bpm)

    def update_tempo(self, bpm):
        """ Schedules the bpm change at the next bar, returns the beat and start time of the next change """
        try:
            assert bpm > 0 and bpm < 10000, "Tempo must be a reasonable positive number"
        except AssertionError as err:
            raise (ValueError(err))

        next_bar = self.next_bar()
        bpm_start_time = self.get_time_at_beat(next_bar)
        bpm_start_beat = next_bar

        def func():
            # object.__setattr__(self, "bpm", self._convert_json_bpm(bpm))
            self.last_now_call = self.bpm_start_time = bpm_start_time
            self.bpm_start_beat = bpm_start_beat

        # Give next bar value to bpm_start_beat
        self.schedule(func, next_bar, is_priority=True)

        return bpm_start_beat, bpm_start_time

    # def update_tempo_from_connection(self, bpm, bpm_start_beat, bpm_start_time, schedule_now=False):
    #     """ Sets the bpm externally from another connected instance of FoxDot """
    #
    #     def func():
    #         self.last_now_call = self.bpm_start_time = self.get_time_at_beat(bpm_start_beat)
    #         self.bpm_start_beat = bpm_start_beat
    #         object.__setattr__(self, "bpm", self._convert_json_bpm(bpm))
    #
    #     # Might be changing immediately
    #     if schedule_now:
    #         func()
    #     else:
    #         self.schedule(func, is_priority=True)
    #     return None
    #
    # def update_network_tempo(self, bpm, start_beat, start_time):
    #     """ Updates connected FoxDot instances (client or servers) tempi """
    #
    #     json_value = self._convert_bpm_json(bpm)
    #     # If this is a client, send info to server
    #     if self.tempo_client is not None:
    #         self.tempo_client.update_tempo(json_value, start_beat, start_time)
    #     # If this is a server, send info to clients
    #     if self.tempo_server is not None:
    #         self.tempo_server.update_tempo(None, json_value, start_beat, start_time)
    #
    #     return None

    # def set_cpu_usage(self, value):
    #     """ Sets the `sleep_time` attribute to values based on desired high/low/medium cpu usage """
    #     assert 0 <= value <= 2
    #     self.sleep_time_between_updates = self.sleep_values[value]
    #     return None

    # def set_latency(self, value):
    #     """ Sets the `latency` attribute to values based on desired high/low/medium latency """
    #     assert 0 <= value <= 2
    #     self.latency = self.latency_values[value]
    #     return None

    def __setattr__(self, attr, value):
        if attr == "bpm" and self.__setup:
            # Schedule for next bar
            start_beat, start_time = self.update_tempo(value)
        elif attr == "midi_nudge" and self.__setup:
            # Adjust nudge for midi devices
            self.server.set_midi_nudge(value)
            object.__setattr__(self, "midi_nudge", value)
        else:
            self.__dict__[attr] = value
        return

    def bar_length(self):
        """ Returns the length of a bar in terms of beats """
        return (float(self.meter[0]) / self.meter[1]) * 4

    def bars(self, n=1):
        """ Returns the number of beats in 'n' bars """
        return self.bar_length() * n

    def beat_dur(self, n=1):
        """ Returns the length of n beats in seconds """
        return 0 if n == 0 else (60.0 / self.get_bpm()) * n

    def beats_to_seconds(self, beats):
        return self.beat_dur(beats)

    def seconds_to_beats(self, seconds):
        """ Returns the number of beats that occur in a time period  """
        return (self.get_bpm() / 60.0) * seconds

    def get_bpm(self):
        """ Returns the current beats per minute as a floating point number """
        if isinstance(self.bpm, TimeVar):
            bpm_val = self.bpm.now(self.beat)
        else:
            bpm_val = self.bpm
        return float(bpm_val)

    def get_latency(self):
        """ Returns self.latency (which is in seconds) as a fraction of a beat """
        return self.seconds_to_beats(self.latency)

    def get_elapsed_beats_from_last_bpm_change(self):
        """ Returns the number of beats that *should* have elapsed since the last tempo change """
        return float(self.get_elapsed_seconds_from_last_bpm_change() * (self.get_bpm() / 60))

    def get_elapsed_seconds_from_last_bpm_change(self):
        """ Returns the time since the last change in bpm """
        return self.get_time() - self.bpm_start_time

    def get_time(self):
        """ Returns current machine clock time with nudges values added """
        return time.time() + float(self.nudge) + float(self.hard_nudge)

    def get_time_at_beat(self, beat):
        """ Returns the time that the local computer's clock will be at 'beat' value """
        if isinstance(self.bpm, TimeVar):
            t = self.get_time() + self.beat_dur(beat - self.now())
        else:
            t = self.bpm_start_time + self.beat_dur(beat - self.bpm_start_beat)
        return t

    def sync_to_midi(self, port=0, sync=True):
        """ If there is an available midi-in device sending MIDI Clock messages,
            this attempts to follow the tempo of the device. Requies rtmidi """
        try:
            if sync:
                self.midi_clock = MidiIn(port)
            elif self.midi_clock:
                self.midi_clock.close()
                self.midi_clock = None
        except MIDIDeviceNotFound as e:
            print("{}: No MIDI devices found".format(e))
        return

    def debug(self, on=True):
        """ Toggles debugging information printing to console """
        self.debugging = bool(on)
        return

    def set_time(self, beat):
        """ Set the clock time to 'beat' and update players in the clock """
        self.start_time = time.time()
        self.scheduling_queue.clear()
        self.beat = beat
        self.bpm_start_beat = beat
        self.bpm_start_time = self.start_time
        # self.time = time() - self.start_time
        for player in self.playing:
            player(count=True)
        return

    def calculate_nudge(self, time1, time2, latency):
        """ Approximates the nudge value of this TempoClock based on the machine time.time()
            value from another machine and the latency between them """
        # self.hard_nudge = time2 - (time1 + latency)
        self.hard_nudge = time1 - time2 - latency
        return

    def _convert_bpm_json(self, bpm):
        if isinstance(bpm, (int, float)):
            return float(bpm)
        elif isinstance(bpm, TimeVar):
            return bpm.json_value()

    def json_bpm(self):
        """ Returns the bpm in a data type that can be sent over json"""
        return self._convert_bpm_json(self.bpm)

    def get_sync_info(self):
        """ Returns information for synchronisation across multiple FoxDot instances. To be
            stored as a JSON object with a "sync" header """
        data = {
            "sync": {
                "bpm_start_time": float(self.bpm_start_time),
                "bpm_start_beat": float(self.bpm_start_beat),
                "bpm": self.json_bpm(),
            }
        }
        return data



    def mod(self, beat, t=0):
        """ Returns the next time at which `Clock.now() % beat` will equal `t` """
        n = self.now() // beat
        return (n + 1) * beat + t

    def osc_message_time(self):
        """ Returns the true time that an osc message should be run i.e. now + latency """
        return time.time() + self.latency



    # def _adjust_hard_nudge(self):
    #     """ Checks for any drift between the current beat value and the value
    #         expected based on time elapsed and adjusts the hard_nudge value accordingly """
    #
    #     beats_elapsed = int(self.now()) - self.bpm_start_beat
    #     expected_beat = self.get_elapsed_beats_from_last_bpm_change()
    #     # Dont adjust nudge on first bar of tempo change
    #     if beats_elapsed > 0:
    #         # Account for nudge in the drift
    #         self.drift = self.beat_dur(expected_beat - beats_elapsed) - self.nudge
    #         if abs(self.drift) > 0.001:  # value could be reworked / not hard coded
    #             self.hard_nudge -= self.drift
    #     return self._schedule_adjust_hard_nudge()

    # def _schedule_adjust_hard_nudge(self):
    #     """ Start recursive call to adjust hard-nudge values """
    #     return self.schedule(self._adjust_hard_nudge)






    def future(self, dur, obj, args=(), kwargs={}):
        """ Add a player / event to the queue `dur` beats in the future """
        self.schedule(obj, self.now() + dur, args, kwargs)
        return

    def next_bar(self):
        """ Returns the beat value for the start of the next bar """
        beat = self.now()
        return beat + (self.meter[0] - (beat % self.meter[0]))

    def next_event(self):
        """ Returns the beat index for the next event to be called """
        return self.scheduling_queue[-1][1]

    def call(self, obj, dur, args=()):
        """ Returns a 'schedulable' wrapper for any callable object """
        return Wrapper(self, obj, dur, args)

    def players(self, ex=[]):
        return [p for p in self.playing if p not in ex]

    # Every n beats, do...
    def every(self, n, cmd, args=()):
        def event(f, n, args):
            f(*args)
            self.schedule(event, self.now() + n, (f, n, args))
            return

        self.schedule(event, self.now() + n, args=(cmd, n, args))
        return None

    def stop(self):
        self.ticking = False
        self.kill_tempo_server()
        self.kill_tempo_client()
        self.clear()
        return None

    def shift(self, n):
        """ Offset the clock time """
        self.beat += n
        return None

    def swing(self, amount=0.1):
        """ Sets the nudge attribute to var([0, amount * (self.bpm / 120)],1/2)"""
        self.nudge = TimeVar([0, amount * (self.bpm / 120)], 1 / 2) if amount != 0 else 0
        return None

    def clear(self):
        """ Remove players from clock """
        self.items = []
        self.scheduling_queue.clear()
        self.solo.reset()

        for player in list(self.playing):
            player.kill()

        # for item in self.items:
        #     if hasattr(item, 'stop'):
        #         item.stop()

        self.playing = []
        return None

