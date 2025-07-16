#!/usr/bin/env python3
"""
Test script for fixed PersistentPointInTime behavior with derived points
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the fixed implementation
from src.renardo.lib.TempoClock.clock import PointInTime, PersistentPointInTime, RecurringPointInTime, TempoClock
from src.renardo.lib.TempoClock.point_in_time_registry import registry

def test_persistent_derived_points():
    """Test that derived points from PersistentPointInTime are correctly notified on multiple triggers"""
    print("=== Testing PersistentPointInTime with Derived Points ===")
    
    # Create a clock
    clock = TempoClock()
    clock.server = None  # Avoid server issues
    
    # Create persistent point and derived point
    base_point = PersistentPointInTime()
    derived_point = base_point + 16  # Should be notified when base_point is triggered
    
    print(f"Created base point: {base_point}")
    print(f"Created derived point (base + 16): {derived_point}")
    
    # Test execution logs
    base_executions = []
    derived_executions = []
    
    # Create test functions
    def base_func():
        base_executions.append(f"Base function executed at beat {clock.now()}")
        print(f"*** Base function executed at beat {clock.now()} ***")
    
    def derived_func():
        derived_executions.append(f"Derived function executed at beat {clock.now()}")
        print(f"*** Derived function (+16) executed at beat {clock.now()} ***")
    
    # Schedule functions
    clock.schedule(base_func, base_point)
    clock.schedule(derived_func, derived_point)
    
    print(f"After scheduling: Base has {len(base_point._schedulables)} schedulables")
    print(f"After scheduling: Derived has {len(derived_point._schedulables)} schedulables")
    
    # First trigger
    print("\n--- First trigger at beat 10 ---")
    base_point.beat = 10
    # Simulate clock advancing
    clock.beat = 10
    print(f"Base executions: {base_executions}")
    # Advance to derived point time
    print("\n--- Advancing to derived point (beat 26) ---")
    clock.beat = 26
    print(f"Derived executions: {derived_executions}")
    
    # Registry status
    print("\n--- Registry status after first trigger ---")
    print(f"Derived points for base: {len(registry.get_derived_points(base_point))}")
    
    # Second trigger
    print("\n--- Second trigger at beat 50 ---")
    base_executions.clear()
    derived_executions.clear()
    base_point.beat = 50
    # Simulate clock advancing
    clock.beat = 50
    print(f"Base executions: {base_executions}")
    # Advance to derived point time
    print("\n--- Advancing to derived point (beat 66) ---")
    clock.beat = 66
    print(f"Derived executions: {derived_executions}")

def test_multiple_derived_points():
    """Test with multiple derived points at different offsets"""
    print("\n=== Testing PersistentPointInTime with Multiple Derived Points ===")
    
    # Create a clock
    clock = TempoClock()
    clock.server = None
    
    # Create persistent point and multiple derived points
    break_point = PersistentPointInTime()
    before_break = break_point - 8  # 8 beats before break
    after_break = break_point + 16  # 16 beats after break
    
    # Execution logs
    before_executions = []
    main_executions = []
    after_executions = []
    
    # Create test functions
    def before_func():
        before_executions.append(f"Before break at beat {clock.now()}")
        print(f"*** 8 beats before break at beat {clock.now()} ***")
    
    def main_func():
        main_executions.append(f"Break point at beat {clock.now()}")
        print(f"*** Break point at beat {clock.now()} ***")
    
    def after_func():
        after_executions.append(f"After break at beat {clock.now()}")
        print(f"*** 16 beats after break at beat {clock.now()} ***")
    
    # Schedule functions
    clock.schedule(before_func, before_break)
    clock.schedule(main_func, break_point)
    clock.schedule(after_func, after_break)
    
    # First trigger sequence
    print("\n--- First break sequence starting at beat 32 ---")
    break_point.beat = 32
    
    # Simulate clock advancing through all points
    print("Advancing to before_break (beat 24)")
    clock.beat = 24
    print(f"Before executions: {before_executions}")
    
    print("Advancing to break_point (beat 32)")
    clock.beat = 32
    print(f"Main executions: {main_executions}")
    
    print("Advancing to after_break (beat 48)")
    clock.beat = 48
    print(f"After executions: {after_executions}")
    
    # Reset logs for second sequence
    before_executions.clear()
    main_executions.clear()
    after_executions.clear()
    
    # Second trigger sequence
    print("\n--- Second break sequence starting at beat 64 ---")
    break_point.beat = 64
    
    # Simulate clock advancing through all points again
    print("Advancing to before_break (beat 56)")
    clock.beat = 56
    print(f"Before executions: {before_executions}")
    
    print("Advancing to break_point (beat 64)")
    clock.beat = 64
    print(f"Main executions: {main_executions}")
    
    print("Advancing to after_break (beat 80)")
    clock.beat = 80
    print(f"After executions: {after_executions}")

if __name__ == "__main__":
    test_persistent_derived_points()
    test_multiple_derived_points()
    
    print("\n🎉 All tests completed!")