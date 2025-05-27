#!/usr/bin/env python3
"""
Test script for PersistentPointInTime and RecurringPointInTime classes
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from renardo.lib.TempoClock.clock import PointInTime, PersistentPointInTime, RecurringPointInTime, TempoClock

def test_persistent_point_in_time():
    """Test PersistentPointInTime functionality"""
    print("=== Testing PersistentPointInTime ===")
    
    # Create a clock
    clock = TempoClock()
    clock.server = None  # Avoid server issues
    
    # Create persistent point
    persistent_pit = PersistentPointInTime()
    print(f"Created: {persistent_pit}")
    
    # Create test functions
    execution_log = []
    
    def test_func1():
        execution_log.append("Function 1 executed")
        print("*** Function 1 executed ***")
    
    def test_func2():
        execution_log.append("Function 2 executed")
        print("*** Function 2 executed ***")
    
    # Schedule functions
    clock.schedule(test_func1, persistent_pit)
    clock.schedule(test_func2, persistent_pit)
    
    print(f"After scheduling: {persistent_pit}")
    print(f"Schedulables: {len(persistent_pit._schedulables)}")
    
    # First trigger
    print("\n--- First trigger ---")
    persistent_pit.beat = 10
    print(f"After first trigger: {persistent_pit}")
    print(f"Execution log: {execution_log}")
    print(f"Is defined: {persistent_pit.is_defined}")
    print(f"Schedulables: {len(persistent_pit._schedulables)}")
    print(f"To be scheduled: {len(clock.to_be_scheduled)}")
    
    # Second trigger
    print("\n--- Second trigger ---")
    execution_log.clear()
    persistent_pit.beat = 20
    print(f"After second trigger: {persistent_pit}")
    print(f"Execution log: {execution_log}")
    print(f"Is defined: {persistent_pit.is_defined}")

def test_recurring_point_in_time():
    """Test RecurringPointInTime functionality"""
    print("\n=== Testing RecurringPointInTime ===")
    
    # Create a clock
    clock = TempoClock()
    clock.server = None  # Avoid server issues
    
    # Create recurring point with 4-beat period
    recurring_pit = RecurringPointInTime(period=4)
    print(f"Created: {recurring_pit}")
    
    # Create test function
    execution_log = []
    
    def recurring_func():
        execution_log.append(f"Recurring function executed at beat {clock.now()}")
        print(f"*** Recurring function executed at beat {clock.now()} ***")
    
    # Schedule function
    clock.schedule(recurring_func, recurring_pit)
    
    print(f"After scheduling: {recurring_pit}")
    print(f"Schedulables: {len(recurring_pit._schedulables)}")
    
    # First trigger
    print("\n--- First trigger ---")
    recurring_pit.beat = 8
    print(f"After first trigger: {recurring_pit}")
    print(f"Execution log: {execution_log}")
    print(f"Is defined: {recurring_pit.is_defined}")
    print(f"Clock queue length: {len(clock.scheduling_queue)}")
    print(f"To be scheduled: {len(clock.to_be_scheduled)}")
    
    print("\n--- Simulating clock advance ---")
    print("Setting clock time to 12 (should trigger second execution)")
    clock.beat = 12
    print(f"Clock time: {clock.now()}")
    print(f"Recurring point after clock advance: {recurring_pit}")

def test_arithmetic_with_new_classes():
    """Test arithmetic operations with new PointInTime classes"""
    print("\n=== Testing Arithmetic with New Classes ===")
    
    # Test persistent with arithmetic
    persistent_pit = PersistentPointInTime()
    arithmetic_result = persistent_pit + 5
    print(f"persistent_pit + 5 = {arithmetic_result}")
    print(f"Type: {type(arithmetic_result)}")
    
    # Test recurring with arithmetic  
    recurring_pit = RecurringPointInTime(period=8)
    arithmetic_result2 = recurring_pit * 2
    print(f"recurring_pit * 2 = {arithmetic_result2}")
    print(f"Type: {type(arithmetic_result2)}")

if __name__ == "__main__":
    test_persistent_point_in_time()
    test_recurring_point_in_time()
    test_arithmetic_with_new_classes()
    
    print("\n🎉 All tests completed!")