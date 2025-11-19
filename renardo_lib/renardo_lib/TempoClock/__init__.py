"""
    Clock management for scheduling notes and functions. Anything 'callable', such as a function
    or instance with a `__call__` method, can be scheduled. An instance of `TempoClock` is created
    when FoxDot started up called `Clock`, which is used by `Player` instances to schedule musical
    events. 

    The `TempoClock` is also responsible for sending the osc messages to SuperCollider. It contains
    a queue of event blocks, instances of the `QueueBlock` class, which themselves contain queue
    items, instances of the `QueueObj` class, which themseles contain the actual object or function
    to be called. The `TempoClock` is continually running and checks if any queue block should 
    be activated. A queue block has a "beat" value for which its contents should be activated. To make
    sure that events happen on time, the `TempoClock` will begin processing the contents 0.25
    seconds before it is *actually* meant to happen in case there is a large amount to process.  When 
    a queue block is activated, a new thread is created to process all of the callable objects it
    contains. If it calls a `Player` object, the queue block keeps track of the OSC messages generated 
    until all `Player` objects in the block have been called. At this point the thread is told to
    sleep until the remainder of the 0.25 seconds has passed. This value is stored in `Clock.latency`
    and is adjustable. If you find that there is a noticeable jitter between events, i.e. irregular
    beat lengths, you can increase the latency by simply evaluating the following in FoxDot:

        Clock.latency = 0.5

    To stop the clock from scheduling further events, use the `Clock.clear()` method, which is
    bound to the shortcut key, `Ctrl+.`. You can schedule non-player objects in the clock by
    using `Clock.schedule(func, beat, args, kwargs)`. By default `beat` is set to the next
    bar in the clock, but you use `Clock.now() + n` or `Clock.next_bar() + n` to schedule a function
    in the future at a specific time. 

    To change the tempo of the clock, just set the bpm attribute using `Clock.bpm=val`. The change
    in tempo will occur at the start of the next bar so be careful if you schedule this action within
    a function like this:

        def myFunc():
            print("bpm change!")
            Clock.bpm+=50

    This will print the string `"bpm change"` at the next bar and change the bpm value at the
    start of the *following* bar. The reason for this is to make it easier for calculating
    currently clock times when using a `TimeVar` instance (See docs on TimeVar.py) as a tempo.

    You can change the clock's time signature as you would change the tempo by setting the
    `meter` attribute to a tuple with two values. So for 3/4 time you would use the follwing
    code:

        Clock.meter = (3,4)

"""

from __future__ import absolute_import, division, print_function

import time
from traceback import format_exc as error_stack

import sys
import threading
import inspect

from .SchedulingQueue import Queue, SoloPlayer, History, ScheduleError, Wrapper
from renardo_lib.Players import Player
from renardo_lib.Repeat import MethodCall
from renardo_lib.Patterns import asStream
from renardo_lib.TimeVar import TimeVar
from renardo_lib.Midi import MidiIn, MIDIDeviceNotFound
from renardo_lib.Utils import modi
from renardo_lib.ServerManager import ServerManager
from renardo_lib.Settings import CPU_USAGE

# Ableton Link support (optional dependency)
try:
    import link as ableton_link
    LINK_AVAILABLE = True
except ImportError:
    LINK_AVAILABLE = False

class TempoClock(object):

    def __init__(self, bpm=120.0, meter=(4,4)):

        # Flag this when done init
        self.__setup   = False

        # debug information

        self.largest_sleep_time = 0
        self.last_block_dur = 0.0

        self.beat = float(0)  # Beats elapsed (kept for legacy compatibility)
        self.last_now_call = float(0)
        self.ticking = True

        # Player Objects stored here
        self.playing = []

        # Store history of osc messages and functions in here
        self.history = History()

        # All other scheduled items go here
        self.items   = []

        # General set up
        self.bpm   = bpm
        self.meter = meter

        # Create the queue
        self.queue = Queue(clock=self)
        self.current_block = None

        # Flag for next_bar wrapper
        self.now_flag  = False

        # Can be configured
        self.latency_values = [0.25, 0.5, 0.75]
        self.latency    = 0.25 # Time between starting processing osc messages and sending to server
        self.latency_beats = 0.5  # Latency expressed in beats (for dynamic adjustment when BPM changes)
        self.reference_bpm = bpm  # Reference BPM used to calculate latency in seconds from beats
        self.nudge      = 0.0  # If you want to synchronise with something external, adjust the nudge
        self.hard_nudge = 0.0

        self.bpm_start_time = time.time()
        self.bpm_start_beat = 0

        # The duration to sleep while continually looping
        self.sleep_values = [0.01, 0.001, 0.0001]
        self.sleep_time = self.sleep_values[CPU_USAGE]
        self.midi_nudge = 0

        # Debug
        self.debugging = False
        self.__setup   = True

        # If one object is going to be played
        self.solo = SoloPlayer()
        self.thread = threading.Thread(target=self.run)

        # Ableton Link integration
        self.link = None
        self.link_enabled = False
        self.link_sync_interval = 1  # Sync every 1 beat by default

        # Deprecated network sync attributes (kept for backward compatibility)
        self.waiting_for_sync = False  # Legacy: was used for network sync

        # === 2-THREAD ARCHITECTURE STATE ===
        # Thread-safe beat tracking for 2-thread model
        self._beat_lock = threading.RLock()
        self._current_beat = 0.0  # Shared beat state (protected by _beat_lock)
        self._last_update_time = time.time()  # Last time we updated beat

        # BPM state management (protected by _bpm_lock)
        self._bpm_lock = threading.RLock()

        # Thread references
        self._timing_thread = None
        self._scheduling_thread = None
        self._timing_thread_active = False
        self._scheduling_thread_active = False


    @classmethod
    def set_server(cls, server):
        """ Sets the destination for OSC messages being compiled (the server is also the class
            that compiles them) via objects in the clock. Should be an instance of ServerManager -
            see ServerManager.py for more. """
        assert isinstance(server, ServerManager)
        cls.server = server
        return

    @classmethod
    def add_method(cls, func):
        """Add a custom method to the TempoClock class dynamically"""
        setattr(cls, func.__name__, func)

    # ===== Ableton Link Integration =====

    def sync_to_link(self, enabled=True, sync_interval=1):
        """Enable synchronization with Ableton Link.

        Args:
            enabled (bool): Enable/disable Link session
            sync_interval (float): How often to sync (in beats). Default is 1 beat.

        Example:
            Clock.sync_to_link()  # Enable Link sync at current BPM
            Clock.sync_to_link(sync_interval=0.25)  # Sync every quarter beat
        """
        if not LINK_AVAILABLE:
            print("Error: LinkPython not installed. Install with: pip install LinkPython-extern")
            return False

        try:
            # Create Link instance if not exists
            if self.link is None:
                self.link = ableton_link.Link(self.get_bpm())

                # Set up callbacks
                def on_tempo_change(bpm):
                    """Callback when Link tempo changes"""
                    if abs(bpm - self.get_bpm()) > 0.01:
                        if self.debugging:
                            print(f"Link tempo changed to {bpm:.2f} BPM")
                        # Schedule tempo change at next bar
                        self.bpm = bpm

                def on_num_peers_change(num_peers):
                    """Callback when Link peers connect/disconnect"""
                    if self.debugging:
                        print(f"Link peers: {num_peers}")

                def on_start_stop_change(is_playing):
                    """Callback when Link play state changes"""
                    if self.debugging:
                        print(f"Link playback: {'playing' if is_playing else 'stopped'}")

                self.link.setTempoCallback(on_tempo_change)
                self.link.setNumPeersCallback(on_num_peers_change)
                self.link.setStartStopCallback(on_start_stop_change)

            # Enable Link session
            self.link.enabled = enabled
            self.link.startStopSyncEnabled = True
            self.link_enabled = enabled
            self.link_sync_interval = sync_interval

            # Sync initial tempo to Link
            session = self.link.captureSessionState()
            link_time = self.link.clock().micros()
            session.setTempo(self.get_bpm(), link_time)
            self.link.commitSessionState(session)

            # Start periodic sync
            if enabled:
                self.schedule(self._link_sync_update, self.next_bar())
                print(f"Ableton Link enabled at {self.get_bpm():.2f} BPM (peers: {self.link.numPeers()})")

            return True

        except Exception as e:
            print(f"Error enabling Link: {e}")
            return False

    def disable_link(self):
        """Disable Ableton Link synchronization."""
        if self.link is not None:
            self.link.enabled = False
            self.link_enabled = False
            print("Ableton Link disabled")
        return

    def _link_sync_at_beat(self, beat):
        """Synchronization with Ableton Link called at each beat from main loop.
        This replaces the periodic sync for better responsiveness.

        IMPROVED: Better drift correction to prevent slow desynchronization.

        Args:
            beat: Current beat from the clock
        """
        if not self.link_enabled or self.link is None:
            return

        try:
            # Capture Link session state
            session = self.link.captureSessionState()
            link_time = self.link.clock().micros()

            # Get Link's current tempo
            link_tempo = session.tempo()
            current_tempo = self.get_bpm()

            # === TEMPO SYNC ===
            tempo_diff = abs(link_tempo - current_tempo)
            if tempo_diff > 0.01:
                # Link has different tempo - update ours
                if self.debugging:
                    print(f"[Link Tempo Sync @beat {int(beat)}] {current_tempo:.2f} → {link_tempo:.2f} BPM (diff: {tempo_diff:.3f})")
                self.bpm = link_tempo
                # Reset the BPM start time to now to avoid accumulation
                self.bpm_start_time = time.time()
                self.bpm_start_beat = beat
                # Adjust latency to maintain constant beat-based latency with new BPM
                self.update_latency_for_bpm(link_tempo)

            # === BEAT/PHASE SYNC (IMPROVED) ===
            # Use quantum=1 for beat-by-beat sync
            link_beat = session.beatAtTime(link_time, 1)
            clock_beat = beat

            # Calculate drift (difference between Link and our clock)
            beat_drift = link_beat - clock_beat

            if self.debugging:
                link_phase_4 = session.phaseAtTime(link_time, 4)
                clock_phase_4 = clock_beat % 4
                print(f"[Link Sync @beat {int(beat)}] Link: {link_beat:.3f} | Clock: {clock_beat:.3f} | "
                      f"Drift: {beat_drift:+.4f} beats ({beat_drift*500:.2f}ms @ 120BPM)")

            # === IMPROVED DRIFT CORRECTION ===
            # This is the key fix: more aggressive correction to prevent slow drift
            drift_threshold = 0.005  # Tighter threshold (5ms at 120 BPM)

            if abs(beat_drift) > drift_threshold:
                # Always correct drift, not just at bar boundaries
                # Use proportional-integral style correction

                clock_phase = clock_beat % 4
                is_at_bar_start = (clock_phase < 0.1)  # Close to bar start

                if is_at_bar_start or abs(beat_drift) > 0.05:
                    # At bar start OR significant drift: strong correction
                    if self.debugging:
                        print(f"[Link Sync STRONG] Resync beat: {clock_beat:.4f} → {link_beat:.4f} (drift: {beat_drift:+.4f})")

                    # Reset beat position to match Link exactly
                    with self._beat_lock:
                        self._current_beat = link_beat
                        self.beat = link_beat

                    # Also reset the beat tracking reference
                    self.bpm_start_beat = link_beat
                    self.bpm_start_time = time.time()

                else:
                    # Mid-bar but noticeable drift: use nudge correction
                    # MORE AGGRESSIVE: correct 10% of drift per beat instead of 0.1%
                    # At 120 BPM, beats come every 0.5s, so we correct quickly
                    correction_factor = 0.1  # Correct 10% of drift per beat
                    nudge_correction = beat_drift * correction_factor / 60.0  # Convert beats to seconds

                    if abs(nudge_correction) > 0.0001:
                        self.nudge += nudge_correction

                        if self.debugging:
                            print(f"[Link Sync NUDGE] Correction: {nudge_correction:+.6f}s (total nudge: {self.nudge:+.6f}s) | "
                                  f"Drift remaining: {(beat_drift * (1-correction_factor)):+.4f}")

            # === PERIODIC FULL RESYNC (Safety net) ===
            # Every 32 beats, do a full resync even if drift is small
            # This prevents accumulation of tiny errors
            beat_int = int(beat)
            if beat_int > 0 and beat_int % 32 == 0:
                if self.debugging:
                    print(f"[Link Sync PERIODIC] Full resync at beat {beat_int}")

                link_beat_periodic = session.beatAtTime(link_time, 1)
                with self._beat_lock:
                    self._current_beat = link_beat_periodic
                    self.beat = link_beat_periodic

                self.bpm_start_beat = link_beat_periodic
                self.bpm_start_time = time.time()

        except Exception as e:
            if self.debugging:
                print(f"[Link Sync Error @beat {int(beat)}] {e}")
                import traceback
                traceback.print_exc()

    def _link_sync_update(self):
        """DEPRECATED: Old periodic synchronization method.
        Now using _link_sync_at_beat() called from main loop.
        Kept for backward compatibility.
        """
        if not self.link_enabled or self.link is None:
            return

        # This method is no longer used with the new per-beat sync
        # Re-schedule if still needed for some reason
        if hasattr(self, 'link_sync_interval'):
            self.schedule(self._link_sync_update, self.now() + self.link_sync_interval)

    def link_status(self):
        """Display current Ableton Link status."""
        if not LINK_AVAILABLE:
            print("LinkPython not installed")
            return

        if self.link is None or not self.link_enabled:
            print("Ableton Link is disabled")
            return

        try:
            session = self.link.captureSessionState()
            link_time = self.link.clock().micros()

            tempo = session.tempo()
            beat = session.beatAtTime(link_time, 4)
            phase = session.phaseAtTime(link_time, 4)
            is_playing = session.isPlaying()
            num_peers = self.link.numPeers()

            print(f"=== Ableton Link Status ===")
            print(f"Enabled: {self.link.enabled}")
            print(f"Tempo: {tempo:.2f} BPM")
            print(f"Beat: {beat:.2f}")
            print(f"Phase: {phase:.2f} / 4")
            print(f"Playing: {is_playing}")
            print(f"Peers: {num_peers}")
            print(f"Sync Interval: every {self.link_sync_interval} beat(s)")

        except Exception as e:
            print(f"Error getting Link status: {e}")

    # ===== End Ableton Link Integration =====

    def __str__(self):
        return str(self.queue)

    def __iter__(self):
        for x in self.queue:
            yield x

    def __len__(self):
        return len(self.queue)

    def __contains__(self, item):
        return item in self.items

    def update_tempo_now(self, bpm):
        """Emergency override for updating tempo immediately (not at next bar)"""
        self.last_now_call = self.bpm_start_time = time.time()
        self.bpm_start_beat = self.now()
        object.__setattr__(self, "bpm", bpm)
        # Adjust latency to maintain constant beat-based latency
        self.update_latency_for_bpm(bpm)
        return

    def set_tempo(self, bpm, override=False):
        """Short-hand for update_tempo and update_tempo_now

        Args:
            bpm: New tempo in beats per minute
            override: If True, change immediately; if False, change at next bar
        """
        return self.update_tempo_now(bpm) if override else self.update_tempo(bpm)

    def update_tempo(self, bpm):
        """Schedules the BPM change at the next bar

        Returns the beat and start time of the next change.
        This ensures tempo changes happen at musically sensible moments.
        """
        try:
            assert bpm > 0, "Tempo must be a positive number"
        except AssertionError as err:
            raise ValueError(err)

        next_bar = self.next_bar()
        bpm_start_time = self.get_time_at_beat(next_bar)
        bpm_start_beat = next_bar

        def func():
            """Inner function to update tempo at scheduled time"""
            object.__setattr__(self, "bpm", bpm)
            self.last_now_call = self.bpm_start_time = bpm_start_time
            self.bpm_start_beat = bpm_start_beat

        # Schedule tempo change for next bar
        self.schedule(func, next_bar, is_priority=True)

        return bpm_start_beat, bpm_start_time


    def swing(self, amount=0.1):
        """ Sets the nudge attribute to var([0, amount * (self.bpm / 120)],1/2)"""
        self.nudge = TimeVar([0, amount * (self.bpm / 120)], 1/2) if amount != 0 else 0
        return

    def set_cpu_usage(self, value):
        """ Sets the `sleep_time` attribute to values based on desired high/low/medium cpu usage """
        assert 0 <= value <= 2
        self.sleep_time = self.sleep_values[value]
        return

    def set_latency(self, value):
        """ Sets the `latency` attribute to values based on desired high/low/medium latency """
        assert 0 <= value <= 2
        self.latency = self.latency_values[value]
        return

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

    def update_latency_for_bpm(self, bpm=None):
        """ Adjust latency in seconds to maintain constant latency in beats when BPM changes """
        # Use provided BPM or get current BPM
        if bpm is None:
            bpm = self.get_bpm()
        # Convert latency from beats to seconds based on current BPM
        # latency_seconds = (latency_beats / BPM) * 60
        self.latency = (self.latency_beats / bpm) * 60.0
        if self.debugging:
            print(f"[Latency Adjust] BPM: {bpm:.1f} | Latency: {self.latency:.4f}s ({self.latency_beats:.2f} beats)")
        return

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
        self.queue.clear()
        self.beat = beat
        self.bpm_start_beat = beat
        self.bpm_start_time = self.start_time
        # self.time = time() - self.start_time
        for player in self.playing:
            player(count=True)
        return

    # ===== 2-THREAD ARCHITECTURE METHODS =====

    def get_beat(self):
        """Thread-safe getter for current beat. Called by SchedulingThread and external code."""
        with self._beat_lock:
            return self._current_beat

    def _update_beat(self, now):
        """
        Update current beat based on elapsed time. Called only by TimingThread.
        Handles both fixed BPM and TimeVar (dynamic) BPM modes.

        CRITICAL: When Link is enabled, use Link as the source of truth to prevent drift.

        Args:
            now: Current time from time.time()

        Returns:
            Updated beat value
        """
        with self._beat_lock:
            bpm = self.get_bpm()

            # === IF LINK IS ENABLED: USE LINK AS SOURCE OF TRUTH ===
            # This is crucial to prevent slow drift over time
            if self.link_enabled and self.link is not None:
                try:
                    session = self.link.captureSessionState()
                    link_time = self.link.clock().micros()
                    # Get beat directly from Link - this is the authoritative source
                    self._current_beat = session.beatAtTime(link_time, 1)
                except:
                    # If Link fails, fall back to local calculation
                    pass
            else:
                # === NO LINK: Use local beat calculation ===
                if isinstance(bpm, TimeVar):
                    # TimeVar mode: incremental update
                    delta = now - self._last_update_time
                    self._current_beat += delta * (bpm / 60.0)
                    self._last_update_time = now
                else:
                    # Fixed BPM mode: absolute calculation from reference point
                    elapsed = now - self.bpm_start_time
                    self._current_beat = self.bpm_start_beat + (elapsed * bpm / 60.0)

            # Keep legacy self.beat in sync for backward compatibility
            self.beat = self._current_beat
            self._last_update_time = now

            return self._current_beat

    def _timing_thread_loop(self):
        """
        High-frequency thread for beat counting and Link synchronization.
        Runs at ~10kHz for maximum timing precision.

        Responsibilities:
        - Calculate elapsed time and update beat counter
        - Synchronize with Ableton Link at each integer beat
        - Handle BPM changes

        This thread is completely independent from event scheduling.
        """
        last_beat_sync = -1
        self._timing_thread_active = True

        try:
            while self.ticking:
                now = time.time()

                # Update current beat (thread-safe)
                beat = self._update_beat(now)

                # === ABLETON LINK SYNC AT EACH BEAT ===
                # Sync with Link at every integer beat (not periodically)
                if self.link_enabled and self.link is not None:
                    current_beat_int = int(beat)

                    # Only sync once per beat (when we cross to a new integer beat)
                    if current_beat_int > last_beat_sync:
                        last_beat_sync = current_beat_int
                        self._link_sync_at_beat(beat)

                # High frequency for precision (0.00001 = 10kHz, not too high to avoid CPU saturation)
                # Using a very small sleep keeps CPU usage minimal while maintaining timing precision
                time.sleep(0.0001)  # 0.1ms = 10kHz

        finally:
            self._timing_thread_active = False

    def _scheduling_thread_loop(self):
        """
        Normal-frequency thread for event scheduling and execution.
        Polls the timing thread for current beat and checks queue.

        Responsibilities:
        - Poll current beat from TimingThread
        - Check if events should trigger
        - Spawn worker threads for event blocks

        This thread is completely independent from beat counting.
        """
        self._scheduling_thread_active = True

        try:
            while self.ticking:
                # Get current beat from shared state (thread-safe read)
                beat = self.get_beat()

                # Check if event should trigger
                if self.queue.after_next_event(beat):
                    self.current_block = self.queue.pop()

                    # Spawn worker thread for block execution
                    if len(self.current_block):
                        threading.Thread(
                            target=self.__run_block,
                            args=(self.current_block, beat)
                        ).start()

                # Normal polling frequency (configurable via CPU_USAGE)
                if self.sleep_time > 0:
                    time.sleep(self.sleep_time)

        finally:
            self._scheduling_thread_active = False

    # ===== Core Clock Methods =====

    def _now(self):
        """
        LEGACY METHOD - Kept for backward compatibility.

        In the 2-thread architecture, beat counting is handled by TimingThread.
        This method now redirects to get_beat() which reads from the shared _current_beat.

        If the clock is not ticking, it falls back to calculating the beat manually.
        """
        if self.ticking:
            # Clock is running - get beat from TimingThread
            return self.get_beat()
        else:
            # Clock is stopped - calculate manually (for offline use)
            if isinstance(self.bpm, (int, float)):
                self.beat = self.bpm_start_beat + self.get_elapsed_beats_from_last_bpm_change()
            else:
                now = self.get_time()
                self.beat += (now - self.last_now_call) * (self.get_bpm() / 60)
                self.last_now_call = now
            return self.beat

    def now(self):
        """
        Returns the total elapsed time in beats.

        In the 2-thread architecture, this retrieves the beat from TimingThread's shared state.
        When the clock is not ticking, it falls back to manual calculation.
        """
        if self.ticking:
            # Clock is running - get beat from thread-safe getter
            return float(self.get_beat())
        else:
            # Clock is stopped - calculate manually
            return float(self._now())

    def mod(self, beat, t=0):
        """ Returns the next time at which `Clock.now() % beat` will equal `t` """
        n = self.now() // beat
        return (n + 1) * beat + t 

    def osc_message_time(self):
        """ Returns the true time that an osc message should be run i.e. now + latency """
        return time.time() + self.latency
        
    def start(self):
        """
        Starts the 2-thread architecture: TimingThread and SchedulingThread.

        TimingThread (high-frequency ~10kHz):
        - Counts beats with maximum precision
        - Synchronizes with Ableton Link at each beat
        - Completely independent from event scheduling

        SchedulingThread (normal-frequency ~1kHz):
        - Polls current beat from TimingThread
        - Checks queue for events to trigger
        - Spawns worker threads for event blocks

        This replaces the old single-thread run() loop.
        """
        if self._timing_thread is not None:
            # Threads already started
            return

        self.ticking = True
        self._last_update_time = time.time()

        # Start timing thread (high priority for precision)
        self._timing_thread = threading.Thread(
            target=self._timing_thread_loop,
            name="TempoClock-Timing",
            daemon=True
        )
        self._timing_thread.start()

        # Start scheduling thread
        self._scheduling_thread = threading.Thread(
            target=self._scheduling_thread_loop,
            name="TempoClock-Scheduling",
            daemon=True
        )
        self._scheduling_thread.start()

        if self.debugging:
            print(f"TempoClock started with 2-thread architecture")
            print(f"  - TimingThread: {self._timing_thread.name}")
            print(f"  - SchedulingThread: {self._scheduling_thread.name}")

        return

    def _adjust_hard_nudge(self):
        """ Checks for any drift between the current beat value and the value
            expected based on time elapsed and adjusts the hard_nudge value accordingly """
        
        beats_elapsed = int(self.now()) - self.bpm_start_beat
        expected_beat = self.get_elapsed_beats_from_last_bpm_change()

        # Dont adjust nudge on first bar of tempo change

        if beats_elapsed > 0:

            # Account for nudge in the drift

            self.drift  = self.beat_dur(expected_beat - beats_elapsed) - self.nudge

            if abs(self.drift) > 0.001: # value could be reworked / not hard coded

                self.hard_nudge -= self.drift

        return self._schedule_adjust_hard_nudge()

    def _schedule_adjust_hard_nudge(self):
        """ Start recursive call to adjust hard-nudge values """
        return self.schedule(self._adjust_hard_nudge)

    def __run_block(self, block, beat):
        """ Private method for calling all the items in the queue block.
            This means the clock can still 'tick' while a large number of
            events are activated  """

        # Set the time to "activate" messages on with consistent latency
        # Using absolute time + latency prevents accumulation of timing errors
        # that occur when trying to compensate for late block triggering

        now_real_time = time.time()
        block.time = now_real_time + self.latency

        # Log block execution timing
        if self.debugging:
            print(f"[Block] Beat:{block.beat:.3f} | Now:{beat:.3f} | "
                  f"BlockTime:{block.time:.6f} (now={now_real_time:.6f} + latency={self.latency:.3f}s)")

        # Log OSC timing for Link sync debug
        if self.debugging and self.link_enabled:
            scheduled_time = block.time
            actual_time = now_real_time
            latency_diff = scheduled_time - actual_time
            beat_diff = beat - block.beat

            if self.link:
                session = self.link.captureSessionState()
                link_time_micros = self.link.clock().micros()

                # Beat actuel de Link
                link_beat_now = session.beatAtTime(link_time_micros, 1)

                # Beat théorique de Link au moment où l'OSC sera envoyé (block.time)
                # Convertir scheduled_time (secondes) en microsecondes Link
                scheduled_time_micros = int(scheduled_time * 1_000_000)
                link_beat_theoretical = session.beatAtTime(scheduled_time_micros, 1)

                link_drift_now = link_beat_now - beat
                link_drift_theoretical = link_beat_theoretical - block.beat

                print(f"[OSC Send] Target beat:{block.beat:.3f} | Actual beat:{beat:.3f} | "
                      f"Diff:{beat_diff:+.3f} | Latency:{latency_diff:.3f}s")
                print(f"           Link NOW: {link_beat_now:.3f} (drift:{link_drift_now:+.3f}) | "
                      f"Link THEORETICAL @OSC: {link_beat_theoretical:.3f} (drift:{link_drift_theoretical:+.3f})")

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

        return

    def run(self):
        """
        DEPRECATED: This method is kept for backward compatibility.
        The clock now uses a 2-thread architecture (TimingThread + SchedulingThread).

        The threads are automatically started via the self.thread from __init__().
        This method is only called if the old threading mechanism is used.

        For manual clock control, use:
        - start()  : Start both threads
        - stop()   : Stop both threads
        """
        # The 2-thread loops are now run by separate threads started in start()
        # This method is called by the daemon thread created in __init__(),
        # so we just call start() which will set up both threads
        self.start()

        # Keep this loop for any legacy code that might expect run() to block
        # It will exit when ticking becomes False
        while self.ticking:
            time.sleep(0.1)

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

        self.queue.add(obj, beat, args, kwargs, is_priority)

        # block.time = self.osc_message_accum

        return

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
        return self.queue[-1][1]

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
        return

    def stop(self):
        """
        Stops both TimingThread and SchedulingThread gracefully.

        This method:
        1. Sets ticking=False to signal threads to stop
        2. Waits for both threads to finish (with timeout)
        3. Clears the queue and stops all players
        """
        self.ticking = False

        # Wait for timing thread to stop
        if self._timing_thread is not None and self._timing_thread.is_alive():
            self._timing_thread.join(timeout=1.0)
            self._timing_thread = None

        # Wait for scheduling thread to stop
        if self._scheduling_thread is not None and self._scheduling_thread.is_alive():
            self._scheduling_thread.join(timeout=1.0)
            self._scheduling_thread = None

        # Clean up
        self.kill_tempo_server()
        self.kill_tempo_client()
        self.clear()

        if self.debugging:
            print("TempoClock stopped (both threads terminated)")

        return

    def shift(self, n):
        """ Offset the clock time """
        self.beat += n
        return

    def clear(self):
        """ Remove players from clock """

        self.items = []
        self.queue.clear()
        self.solo.reset()

        # Stop all Ableton clips before killing players
        try:
            import renardo_lib
            # Use the global ableton_project instance if available
            if renardo_lib.ableton_project is not None and hasattr(renardo_lib.ableton_project, 'stop_all_clips'):
                renardo_lib.ableton_project.stop_all_clips()
        except:
            pass  # Silently ignore if Ableton integration is not available

        for player in list(self.playing):

            player.kill()

        # for item in self.items:

        #     if hasattr(item, 'stop'):

        #         item.stop()

        self.playing = []

        return
