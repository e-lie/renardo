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


# The rest of the TempoClock implementation remains the same...
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
        
        # Collection for deferred scheduling when using PointInTime
        self.to_be_scheduled = []

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

    def schedule(self, callable_obj, beat=None, args=(), kwargs={}, is_priority=False):
        """ TempoClock.schedule(callable, beat=None)
            Add a player / event to the queue """
        # Make sure the object can actually be called
        try:
            assert callable(callable_obj)
        except AssertionError:
            raise ScheduleError(callable_obj)

        # Start the clock ticking if not already
        if self.ticking == False:
            self.start()

        # Handle PointInTime instances
        if isinstance(beat, PointInTime):
            schedulable = Schedulable(self, callable_obj, args, kwargs, is_priority)
            beat.add_schedulable(schedulable)
            # Add to to_be_scheduled if the PointInTime is not yet defined
            if not beat.is_defined:
                self.to_be_scheduled.append(schedulable)
            return None

        # Default is next bar
        if beat is None:
            beat = self.next_bar()

        # Keep track of objects in the Clock
        if callable_obj not in self.playing and isinstance(callable_obj, Player):
            self.playing.append(callable_obj)

        if callable_obj not in self.items:
            self.items.append(callable_obj)

        # Add to the queue
        self.scheduling_queue.add(callable_obj, beat, args, kwargs, is_priority)
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
            object.__setattr__(self, "bpm", float(bpm))
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
            # Handle TimeVar bpm differently - set immediately, don't schedule
            if isinstance(value, TimeVar):
                object.__setattr__(self, "bpm", value)
                # Reset timing for TimeVar behavior
                self.last_now_call = self.get_time()
            else:
                # For regular numeric BPM, schedule for next bar - don't set immediately
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
        """Convert BPM to JSON format"""
        if isinstance(bpm, (int, float)):
            return float(bpm)
        elif isinstance(bpm, TimeVar):
            return bpm.json_value()
    
    def _convert_json_bpm(self, data):
        """Convert JSON data back to BPM value (including TimeVar objects)"""
        if isinstance(data, list):
            # This is a TimeVar encoded as [class_name, values, duration]
            cls_name = data[0]
            val = data[1] 
            dur = data[2]
            # Import TimeVar dynamically to avoid circular imports
            return TimeVar(val, dur)
        else:
            # Regular numeric value
            return data

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