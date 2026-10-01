"""
PointInTime and friends.

Represents an undefined-until-triggered beat value that other code can
schedule callables against (`Clock.schedule(func, beat=my_point)`), combine
with arithmetic (`my_point + 8`), or bind together
(`other_point.beat = my_point`, meaning "fire `other_point` whenever
`my_point` does").

Split out of clock.py so that other modules (e.g. osc_trigger.py) can
subclass PersistentPointInTime without importing the whole TempoClock
module and creating a circular import.
"""

from .point_in_time_registry import registry


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
        if isinstance(value, PointInTime):
            # `other.beat = some_point_in_time`: bind rather than treat as a
            # numeric beat value — `self` fires whenever `value` does.
            self._bind_to(value)
            return

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

    def _bind_to(self, source_point):
        """Bind this PointInTime so it (re-)fires whenever `source_point` does.

        Used for syntax like `p.beat = trig("/route")`: instead of trying to
        treat `source_point` as a numeric beat value, register `self` as a
        point derived from it, exactly like `p2 = p1 + 0` would, so it gets
        triggered every time `source_point` becomes defined.
        """
        if source_point.is_defined:
            self.beat = source_point.beat
        else:
            source_point._derived_points.append(self)
            registry.register_derived_point(source_point, self, {'type': 'bind'})

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
        if isinstance(value, PointInTime):
            self._bind_to(value)
            return

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
        if isinstance(value, PointInTime):
            self._bind_to(value)
            return

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
