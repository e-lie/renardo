from __future__ import absolute_import, division, print_function

import time
from traceback import format_exc as error_stack

import sys
import threading

from .scheduling_queue import SchedulingQueue, SoloPlayer, History, ScheduleError, Wrapper
from .point_in_time_registry import registry

from renardo.lib.Player import Player
from renardo.lib.TimeVar import TimeVar
from renardo.sc_backend.Midi import MidiIn, MIDIDeviceNotFound
from renardo.sc_backend import TempoClient, ServerManager
from renardo.settings_manager import settings
from renardo.logger import get_logger

# Ableton Link support (optional dependency)
try:
    import link as ableton_link
    LINK_AVAILABLE = True
except ImportError:
    LINK_AVAILABLE = False

logger = get_logger('lib.TempoClock.clock')


class PointInTime:
    """Represents a point in time that can be undefined or defined with a beat value."""
    
    def __init__(self, beat=None):
        self._beat = beat
        self._schedulables = []
        self._operations = []  # Store operations to apply when beat is defined
        self._derived_points = []  # Track PointInTime objects that depend on this one
    
    @property
    def is_defined(self):
        """Returns True if this point in time has a defined beat value."""
        return self._beat is not None
    
    @property
    def beat(self):
        """Returns the beat value if defined, otherwise None."""
        return self._beat
    
    @beat.setter
    def beat(self, value):
        """Sets the beat value and schedules all pending schedulables."""
        if self._beat is not None:
            raise ValueError("PointInTime is already defined")
        
        # Apply all stored operations to get the final beat value
        final_value = value
        for operation in self._operations:
            final_value = operation.apply(final_value)
        
        self._beat = final_value
        # Schedule all pending schedulables
        for schedulable in self._schedulables:
            schedulable.clock.schedule(
                schedulable.callable_obj,
                beat=final_value,
                args=schedulable.args,
                kwargs=schedulable.kwargs,
                is_priority=schedulable.is_priority
            )
        # Clear the lists after scheduling
        self._schedulables.clear()
        self._operations.clear()
        
        # Notify derived points that might be waiting for this definition
        self._notify_derived_points()
    
    def add_schedulable(self, schedulable):
        """Adds a schedulable to be executed when this point in time is defined."""
        if self.is_defined:
            # If already defined, schedule immediately
            schedulable.clock.schedule(
                schedulable.callable_obj,
                beat=self._beat,
                args=schedulable.args,
                kwargs=schedulable.kwargs,
                is_priority=schedulable.is_priority
            )
        else:
            # Store for later scheduling
            self._schedulables.append(schedulable)
    
    def __repr__(self):
        if self.is_defined:
            return f"PointInTime(beat={self._beat})"
        else:
            ops_str = f", {len(self._operations)} ops" if self._operations else ""
            return f"PointInTime(undefined, {len(self._schedulables)} pending{ops_str})"
    
    def __add__(self, other):
        """Addition operation with numbers or other PointInTime objects."""
        return self._create_operation_result('add', other)
    
    def __radd__(self, other):
        """Right addition for number + PointInTime."""
        return self._create_operation_result('add', other, reverse=True)
    
    def __sub__(self, other):
        """Subtraction operation with numbers or other PointInTime objects."""
        return self._create_operation_result('sub', other)
    
    def __rsub__(self, other):
        """Right subtraction for number - PointInTime."""
        return self._create_operation_result('sub', other, reverse=True)
    
    def __mul__(self, other):
        """Multiplication operation with numbers or other PointInTime objects."""
        return self._create_operation_result('mul', other)
    
    def __rmul__(self, other):
        """Right multiplication for number * PointInTime."""
        return self._create_operation_result('mul', other, reverse=True)
    
    def __truediv__(self, other):
        """Division operation with numbers or other PointInTime objects."""
        return self._create_operation_result('div', other)
    
    def __rtruediv__(self, other):
        """Right division for number / PointInTime."""
        return self._create_operation_result('div', other, reverse=True)
    
    def _create_operation_result(self, op_type, other, reverse=False):
        """Creates a new PointInTime with the operation applied or queued."""
        if isinstance(other, (int, float)):
            # Operation with a number
            if self.is_defined:
                # Apply immediately
                result_beat = self._apply_numeric_operation(self._beat, op_type, other, reverse)
                return PointInTime(result_beat)
            else:
                # Queue the operation
                result = PointInTime()
                result._operations = self._operations.copy()
                result._operations.append(NumericOperation(op_type, other, reverse))
                # Register this result as dependent on self
                self._derived_points.append(result)
                # Register in the global registry
                registry.register_derived_point(self, result, {'type': 'numeric', 'op': op_type, 'value': other, 'reverse': reverse})
                return result
        
        elif isinstance(other, PointInTime):
            # Operation with another PointInTime
            if self.is_defined and other.is_defined:
                # Both defined, apply immediately
                result_beat = self._apply_numeric_operation(self._beat, op_type, other._beat, reverse)
                return PointInTime(result_beat)
            else:
                # At least one undefined, create compound operation
                result = PointInTime()
                result._operations = self._operations.copy()
                result._operations.append(PointInTimeOperation(op_type, other, reverse))
                # Register this result as dependent on both points
                if not self.is_defined:
                    self._derived_points.append(result)
                    # Register in the global registry
                    registry.register_derived_point(self, result, {'type': 'point', 'op': op_type, 'reverse': reverse})
                if not other.is_defined:
                    other._derived_points.append(result)
                    # Register in the global registry
                    registry.register_derived_point(other, result, {'type': 'point', 'op': op_type, 'reverse': reverse})
                return result
        
        else:
            raise TypeError(f"Unsupported operand type for {op_type}: {type(other)}")
    
    def _apply_numeric_operation(self, left_val, op_type, right_val, reverse=False):
        """Applies a numeric operation and returns the result."""
        if reverse:
            left_val, right_val = right_val, left_val
        
        if op_type == 'add':
            return left_val + right_val
        elif op_type == 'sub':
            return left_val - right_val
        elif op_type == 'mul':
            return left_val * right_val
        elif op_type == 'div':
            if right_val == 0:
                raise ZeroDivisionError("Division by zero in PointInTime operation")
            return left_val / right_val
        else:
            raise ValueError(f"Unknown operation type: {op_type}")
    
    def _notify_derived_points(self):
        """Notify derived PointInTime objects that this point has been defined."""
        # Use the global registry to notify derived points
        registry.notify_derived_points(self, self._beat)
        
        # Simple approach: just trigger any derived points that are waiting
        for derived_point in self._derived_points[:]:  # Copy list to avoid modification during iteration
            if not derived_point.is_defined:
                self._try_resolve_derived_point(derived_point)
        
        # Clear the derived points list
        self._derived_points.clear()
    
    def _try_resolve_derived_point(self, derived_point):
        """Try to resolve a derived point by setting its beat based on this point's beat."""
        if self.is_defined and not derived_point.is_defined:
            try:
                # Set the derived point's beat to trigger its operations
                # The operations will be applied automatically by the beat setter
                derived_point.beat = self._beat
                
            except Exception as e:
                print(f"Error resolving derived PointInTime: {e}")
    
    def clear(self):
        """Remove all scheduled operations related to this PointInTime from the clock."""
        # Clear local schedulables
        for schedulable in self._schedulables[:]:  # Copy list to avoid modification during iteration
            # Remove from clock's to_be_scheduled if present
            if hasattr(schedulable, 'clock') and hasattr(schedulable.clock, 'to_be_scheduled'):
                try:
                    schedulable.clock.to_be_scheduled.remove(schedulable)
                except ValueError:
                    pass  # Not in list, that's okay
        
        # Remove from the global registry
        registry.remove_point(self)
        
        # Clear local collections
        self._schedulables.clear()
        self._operations.clear()
        self._derived_points.clear()
        
        # Reset to undefined state
        self._beat = None
        
        return self


class NumericOperation:
    """Represents an operation between a PointInTime and a numeric value."""
    
    def __init__(self, op_type, value, reverse=False):
        self.op_type = op_type
        self.value = value
        self.reverse = reverse
    
    def apply(self, beat_value):
        """Apply this operation to a beat value."""
        left_val = beat_value
        right_val = self.value
        
        if self.reverse:
            left_val, right_val = right_val, left_val
        
        if self.op_type == 'add':
            return left_val + right_val
        elif self.op_type == 'sub':
            return left_val - right_val
        elif self.op_type == 'mul':
            return left_val * right_val
        elif self.op_type == 'div':
            if right_val == 0:
                raise ZeroDivisionError("Division by zero in PointInTime operation")
            return left_val / right_val
        else:
            raise ValueError(f"Unknown operation type: {self.op_type}")
    
    def __repr__(self):
        op_symbol = {'add': '+', 'sub': '-', 'mul': '*', 'div': '/'}[self.op_type]
        if self.reverse:
            return f"{self.value} {op_symbol} <beat>"
        else:
            return f"<beat> {op_symbol} {self.value}"


class PointInTimeOperation:
    """Represents an operation between two PointInTime objects."""
    
    def __init__(self, op_type, other_point, reverse=False):
        self.op_type = op_type
        self.other_point = other_point
        self.reverse = reverse
    
    def apply(self, beat_value):
        """Apply this operation to a beat value."""
        if not self.other_point.is_defined:
            raise ValueError("Cannot apply PointInTime operation: other PointInTime is still undefined")
        
        # Apply any operations on the other point first
        other_value = self.other_point._beat
        for operation in self.other_point._operations:
            other_value = operation.apply(other_value)
        
        left_val = beat_value
        right_val = other_value
        
        if self.reverse:
            left_val, right_val = right_val, left_val
        
        if self.op_type == 'add':
            return left_val + right_val
        elif self.op_type == 'sub':
            return left_val - right_val
        elif self.op_type == 'mul':
            return left_val * right_val
        elif self.op_type == 'div':
            if right_val == 0:
                raise ZeroDivisionError("Division by zero in PointInTime operation")
            return left_val / right_val
        else:
            raise ValueError(f"Unknown operation type: {self.op_type}")
    
    def __repr__(self):
        op_symbol = {'add': '+', 'sub': '-', 'mul': '*', 'div': '/'}[self.op_type]
        if self.reverse:
            return f"{self.other_point} {op_symbol} <beat>"
        else:
            return f"<beat> {op_symbol} {self.other_point}"


class PersistentPointInTime(PointInTime):
    """A PointInTime that remains schedulable after being triggered."""
    
    def __init__(self, beat=None):
        super().__init__(beat)
    
    @PointInTime.beat.setter  
    def beat(self, value):
        """
        Sets the beat value, schedules all pending schedulables, but keeps them for future scheduling.
        This implementation ensures both direct schedulables and derived points work across multiple triggers.
        """        
        # Apply all stored operations to get the final beat value
        final_value = value
        for operation in self._operations:
            final_value = operation.apply(final_value)
        
        # Temporarily set beat to trigger normal scheduling
        self._beat = final_value
        
        # Schedule all pending schedulables but keep them for future scheduling
        for schedulable in list(self._schedulables):  # Make a copy for safe iteration
            # Schedule the callable at the specified beat
            schedulable.clock.schedule(
                schedulable.callable_obj,
                beat=final_value,
                args=schedulable.args,
                kwargs=schedulable.kwargs,
                is_priority=schedulable.is_priority
            )
        
        # Notify derived points using the registry
        registry.notify_derived_points(self, final_value)
        
        # Reset to undefined state for future use but keep schedulables and operations
        self._beat = None
    
    def add_schedulable(self, schedulable):
        """Override add_schedulable to ensure persistence"""
        # For PersistentPointInTime, always add to the list for future use
        if schedulable not in self._schedulables:
            self._schedulables.append(schedulable)
            
        # If already defined, schedule immediately
        if self.is_defined:
            schedulable.clock.schedule(
                schedulable.callable_obj,
                beat=self._beat,
                args=schedulable.args,
                kwargs=schedulable.kwargs,
                is_priority=schedulable.is_priority
            )
    
    def _create_operation_result(self, op_type, other, reverse=False):
        """Override to return PersistentPointInTime instances."""
        if isinstance(other, (int, float)):
            if self.is_defined:
                result_beat = self._apply_numeric_operation(self._beat, op_type, other, reverse)
                return PersistentPointInTime(result_beat)
            else:
                result = PersistentPointInTime()
                result._operations = self._operations.copy()
                result._operations.append(NumericOperation(op_type, other, reverse))
                self._derived_points.append(result)
                # Register in the global registry
                registry.register_derived_point(self, result, {'type': 'numeric', 'op': op_type, 'value': other, 'reverse': reverse})
                return result
        elif isinstance(other, PointInTime):
            if self.is_defined and other.is_defined:
                result_beat = self._apply_numeric_operation(self._beat, op_type, other._beat, reverse)
                return PersistentPointInTime(result_beat)
            else:
                result = PersistentPointInTime()
                result._operations = self._operations.copy()
                result._operations.append(PointInTimeOperation(op_type, other, reverse))
                if not self.is_defined:
                    self._derived_points.append(result)
                    # Register in the global registry
                    registry.register_derived_point(self, result, {'type': 'point', 'op': op_type, 'reverse': reverse})
                if not other.is_defined:
                    other._derived_points.append(result)
                    # Register in the global registry
                    registry.register_derived_point(other, result, {'type': 'point', 'op': op_type, 'reverse': reverse})
                return result
        else:
            raise TypeError(f"Unsupported operand type for {op_type}: {type(other)}")
    
    def clear(self):
        """Remove all scheduled operations for PersistentPointInTime but maintain ability to reschedule."""
        # Remove from clock's to_be_scheduled 
        for schedulable in self._schedulables[:]:
            if hasattr(schedulable, 'clock') and hasattr(schedulable.clock, 'to_be_scheduled'):
                try:
                    schedulable.clock.to_be_scheduled.remove(schedulable)
                except ValueError:
                    pass
        
        # Remove from the global registry
        registry.remove_point(self)
        
        # For PersistentPointInTime, we clear schedulables since they've been moved to to_be_scheduled
        # Operations and derived points are cleared as well
        self._schedulables.clear()
        self._operations.clear() 
        self._derived_points.clear()
        
        # Reset to undefined state
        self._beat = None
        
        return self
    
    def __repr__(self):
        if self.is_defined:
            return f"PersistentPointInTime(beat={self._beat})"
        else:
            ops_str = f", {len(self._operations)} ops" if self._operations else ""
            return f"PersistentPointInTime(undefined, {len(self._schedulables)} pending{ops_str})"


class RecurringPointInTime(PointInTime):
    """A PointInTime that repeats at regular intervals."""
    
    def __init__(self, period, beat=None):
        super().__init__(beat)
        self.period = period
        self._has_been_triggered = False
    
    @PointInTime.beat.setter
    def beat(self, value):
        """Sets the beat value, schedules callables, and sets up recurring execution."""
        # Apply all stored operations to get the final beat value
        final_value = value
        for operation in self._operations:
            final_value = operation.apply(final_value)
        
        self._beat = final_value
        
        # Schedule all pending schedulables
        for schedulable in list(self._schedulables):  # Make a copy for safe iteration
            schedulable.clock.schedule(
                schedulable.callable_obj,
                beat=final_value,
                args=schedulable.args,
                kwargs=schedulable.kwargs,
                is_priority=schedulable.is_priority
            )
        
        # Clear operations on first trigger only
        if not self._has_been_triggered:
            self._operations.clear()
            self._has_been_triggered = True
        
        # Schedule the next recurrence
        if hasattr(self, '_schedulables') and self._schedulables:
            # Get the clock from the first schedulable
            clock = self._schedulables[0].clock
            next_beat = final_value + self.period
            
            # Create a function to trigger the next recurrence
            def trigger_next_recurrence():
                # Reset and trigger again
                self._beat = None  # Reset to undefined
                self.beat = next_beat  # Trigger again
            
            # Schedule the next recurrence
            clock.schedule(trigger_next_recurrence, next_beat)
        
        # Notify derived points using the registry
        registry.notify_derived_points(self, final_value)
    
    def add_schedulable(self, schedulable):
        """Override add_schedulable to ensure persistence"""
        # For RecurringPointInTime, always add to the list for future use
        if schedulable not in self._schedulables:
            self._schedulables.append(schedulable)
            
        # If already defined, schedule immediately
        if self.is_defined:
            schedulable.clock.schedule(
                schedulable.callable_obj,
                beat=self._beat,
                args=schedulable.args,
                kwargs=schedulable.kwargs,
                is_priority=schedulable.is_priority
            )
    
    def _create_operation_result(self, op_type, other, reverse=False):
        """Override to return RecurringPointInTime instances."""
        if isinstance(other, (int, float)):
            if self.is_defined:
                result_beat = self._apply_numeric_operation(self._beat, op_type, other, reverse)
                return RecurringPointInTime(self.period, result_beat)
            else:
                result = RecurringPointInTime(self.period)
                result._operations = self._operations.copy()
                result._operations.append(NumericOperation(op_type, other, reverse))
                self._derived_points.append(result)
                # Register in the global registry
                registry.register_derived_point(self, result, {'type': 'numeric', 'op': op_type, 'value': other, 'reverse': reverse})
                return result
        elif isinstance(other, PointInTime):
            if self.is_defined and other.is_defined:
                result_beat = self._apply_numeric_operation(self._beat, op_type, other._beat, reverse)
                return RecurringPointInTime(self.period, result_beat)
            else:
                result = RecurringPointInTime(self.period)
                result._operations = self._operations.copy()
                result._operations.append(PointInTimeOperation(op_type, other, reverse))
                if not self.is_defined:
                    self._derived_points.append(result)
                    # Register in the global registry
                    registry.register_derived_point(self, result, {'type': 'point', 'op': op_type, 'reverse': reverse})
                if not other.is_defined:
                    other._derived_points.append(result)
                    # Register in the global registry
                    registry.register_derived_point(other, result, {'type': 'point', 'op': op_type, 'reverse': reverse})
                return result
        else:
            raise TypeError(f"Unsupported operand type for {op_type}: {type(other)}")
    
    def clear(self):
        """Remove all scheduled operations for RecurringPointInTime and stop recurring behavior."""
        # Remove from clock's to_be_scheduled
        for schedulable in self._schedulables[:]:
            if hasattr(schedulable, 'clock') and hasattr(schedulable.clock, 'to_be_scheduled'):
                try:
                    schedulable.clock.to_be_scheduled.remove(schedulable)
                except ValueError:
                    pass
        
        # Remove from the global registry
        registry.remove_point(self)
        
        # For RecurringPointInTime, we also need to stop the recurring scheduling
        # This is more complex since the recurring scheduler creates its own scheduled functions
        # For now, we clear the state and let the user know they need to manually stop players
        
        self._schedulables.clear()
        self._operations.clear()
        self._derived_points.clear()
        
        # Reset to undefined state and stop recurring behavior
        self._beat = None
        self._has_been_triggered = False
        
        print(f"RecurringPointInTime cleaned. Note: Any currently playing instruments should be stopped manually.")
        
        return self
    
    def __repr__(self):
        if self.is_defined:
            return f"RecurringPointInTime(beat={self._beat}, period={self.period})"
        else:
            ops_str = f", {len(self._operations)} ops" if self._operations else ""
            return f"RecurringPointInTime(undefined, period={self.period}, {len(self._schedulables)} pending{ops_str})"


class Schedulable:
    """Wraps a callable object with its scheduling parameters."""
    
    def __init__(self, clock, callable_obj, args=(), kwargs=None, is_priority=False):
        if kwargs is None:
            kwargs = {}
        
        self.clock = clock
        self.callable_obj = callable_obj
        self.args = args
        self.kwargs = kwargs
        self.is_priority = is_priority
    
    def __repr__(self):
        return f"Schedulable({self.callable_obj}, args={self.args}, kwargs={self.kwargs}, priority={self.is_priority})"


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
        self.scheduling_queue = SchedulingQueue(clock=self)
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
        self.sleep_time = 0.0001  # Default to high precision
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
        self.link_phase_offset = -0.5  # Phase offset to align Link beats with Renardo (adjustable)

        # Deprecated network sync attributes (kept for backward compatibility)
        self.waiting_for_sync = False  # Legacy: was used for network sync

        # === 2-THREAD ARCHITECTURE STATE ===
        # Thread-safe beat tracking for 2-thread model
        self._beat_lock = threading.RLock()
        self._current_beat = 0.0  # Shared beat state (protected by _beat_lock)
        self._last_update_time = time.time()  # Last time we updated beat

        # Link clock caching to reduce sampling errors
        # Only query Link's clock at beat boundaries, interpolate between
        self._link_beat_reference = 0.0  # Last beat queried from Link
        self._link_time_reference = 0.0  # time.time() when we got _link_beat_reference
        self._link_query_interval = 0.5  # Only query Link every 0.5 seconds (every ~60 beats @ 120 BPM)

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

    def _get_link_beat(self, session, link_time, quantum=1):
        """
        Get beat from Link session with phase offset applied.

        Args:
            session: Link session state
            link_time: Link time in microseconds
            quantum: Quantum for beat alignment (default=1)

        Returns:
            Link beat with phase offset applied
        """
        link_beat = session.beatAtTime(link_time, quantum)
        return link_beat + self.link_phase_offset

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
            link_beat = self._get_link_beat(session, link_time, quantum=1)
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
                        # Reset Link cache reference point when we resync
                        self._link_beat_reference = link_beat
                        self._link_time_reference = time.time()

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

                link_beat_periodic = self._get_link_beat(session, link_time, quantum=1)
                current_time = time.time()
                with self._beat_lock:
                    self._current_beat = link_beat_periodic
                    self.beat = link_beat_periodic
                    # Reset Link cache reference point
                    self._link_beat_reference = link_beat_periodic
                    self._link_time_reference = current_time

                self.bpm_start_beat = link_beat_periodic
                self.bpm_start_time = current_time

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
            beat = self._get_link_beat(session, link_time, quantum=4)
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
        return str(self.scheduling_queue)

    def __iter__(self):
        for x in self.scheduling_queue:
            yield x

    def __len__(self):
        return len(self.scheduling_queue)

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
        self.scheduling_queue.clear()
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
        Uses periodic Link queries + interpolation to avoid sampling jitter.

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
                    # Only query Link periodically to avoid sampling jitter
                    # Between queries, interpolate using known BPM
                    time_since_link_query = now - self._link_time_reference

                    if time_since_link_query > self._link_query_interval or self._link_time_reference == 0.0:
                        # Time to query Link again
                        session = self.link.captureSessionState()
                        link_time = self.link.clock().micros()

                        # Get beat directly from Link - this is the authoritative source
                        link_beat = self._get_link_beat(session, link_time, quantum=1)

                        # Cache this reference point
                        self._link_beat_reference = link_beat
                        self._link_time_reference = now
                        self._current_beat = link_beat

                        if self.debugging:
                            print(f"[Link Query] Beat: {link_beat:.4f} @ {now:.6f}")
                    else:
                        # Interpolate between Link queries using BPM
                        interpolated_beat = self._link_beat_reference + (time_since_link_query * bpm / 60.0)
                        self._current_beat = interpolated_beat
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
                if self.scheduling_queue.after_next_event(beat):
                    self.current_block = self.scheduling_queue.pop()

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
                link_beat_now = self._get_link_beat(session, link_time_micros, quantum=1)

                # Beat théorique de Link au moment où l'OSC sera envoyé (block.time)
                # Convertir scheduled_time (secondes) en microsecondes Link
                scheduled_time_micros = int(scheduled_time * 1_000_000)
                link_beat_theoretical = self._get_link_beat(session, scheduled_time_micros, quantum=1)

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

        self.scheduling_queue.add(obj, beat, args, kwargs, is_priority)

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


    def kill_tempo_server(self):
        """ Stop the tempo server if running """
        if self.tempo_server is not None:
            self.tempo_server.kill()
            self.tempo_server = None
        return
    
    def kill_tempo_client(self):
        """ Stop the tempo client if running """
        if self.tempo_client is not None:
            self.tempo_client.kill()
            self.tempo_client = None
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
        self.scheduling_queue.clear()
        self.solo.reset()

        # Stop all Ableton clips before killing players
        try:
            from renardo import runtime
            # Use the global ableton_project instance if available
            if getattr(runtime, "ableton_project", None) is not None and hasattr(getattr(runtime, "ableton_project", None), 'stop_all_clips'):
                getattr(runtime, "ableton_project", None).stop_all_clips()
        except:
            pass  # Silently ignore if Ableton integration is not available

        for player in list(self.playing):

            player.kill()

        # for item in self.items:

        #     if hasattr(item, 'stop'):

        #         item.stop()

        self.playing = []

        return
