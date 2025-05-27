#!/usr/bin/env python3
"""
Test script for PointInTime arithmetic operations
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from renardo.lib.TempoClock.clock import PointInTime

def test_defined_arithmetic():
    """Test arithmetic operations with defined PointInTime objects"""
    print("=== Testing Defined PointInTime Arithmetic ===")
    
    # Test with numbers
    p1 = PointInTime(10)
    
    result = p1 + 5
    print(f"PointInTime(10) + 5 = {result} (expected: PointInTime(beat=15))")
    assert result.beat == 15
    
    result = p1 - 3
    print(f"PointInTime(10) - 3 = {result} (expected: PointInTime(beat=7))")
    assert result.beat == 7
    
    result = p1 * 2
    print(f"PointInTime(10) * 2 = {result} (expected: PointInTime(beat=20))")
    assert result.beat == 20
    
    result = p1 / 2
    print(f"PointInTime(10) / 2 = {result} (expected: PointInTime(beat=5.0))")
    assert result.beat == 5.0
    
    # Test reverse operations
    result = 5 + p1
    print(f"5 + PointInTime(10) = {result} (expected: PointInTime(beat=15))")
    assert result.beat == 15
    
    result = 20 - p1
    print(f"20 - PointInTime(10) = {result} (expected: PointInTime(beat=10))")
    assert result.beat == 10
    
    # Test with other PointInTime objects
    p2 = PointInTime(5)
    result = p1 + p2
    print(f"PointInTime(10) + PointInTime(5) = {result} (expected: PointInTime(beat=15))")
    assert result.beat == 15
    
    result = p1 - p2
    print(f"PointInTime(10) - PointInTime(5) = {result} (expected: PointInTime(beat=5))")
    assert result.beat == 5
    
    print("✓ All defined arithmetic tests passed!\n")

def test_undefined_arithmetic():
    """Test arithmetic operations with undefined PointInTime objects"""
    print("=== Testing Undefined PointInTime Arithmetic ===")
    
    # Test with numbers
    p1 = PointInTime()  # undefined
    
    result = p1 + 5
    print(f"PointInTime() + 5 = {result}")
    assert not result.is_defined
    assert len(result._operations) == 1
    
    result = p1 - 3
    print(f"PointInTime() - 3 = {result}")
    assert not result.is_defined
    
    result = p1 * 2
    print(f"PointInTime() * 2 = {result}")
    assert not result.is_defined
    
    result = p1 / 2
    print(f"PointInTime() / 2 = {result}")
    assert not result.is_defined
    
    # Test chained operations
    result = (p1 + 5) * 2 - 3
    print(f"(PointInTime() + 5) * 2 - 3 = {result}")
    assert not result.is_defined
    assert len(result._operations) == 3
    
    # Now define the original and check if operations are applied
    p1.beat = 10
    # p1 should now be 10, but result should still be undefined with operations queued
    
    # Test a fresh undefined point with operations, then define it
    p2 = PointInTime()
    result = (p2 + 5) * 2
    print(f"Before defining: (PointInTime() + 5) * 2 = {result}")
    
    # Now define p2 and check the result
    p2.beat = 3  # (3 + 5) * 2 = 16
    # result should still be undefined since it's a different object
    assert not result.is_defined
    
    print("✓ All undefined arithmetic tests passed!\n")

def test_operation_application():
    """Test that operations are applied correctly when beat is set"""
    print("=== Testing Operation Application ===")
    
    p1 = PointInTime()
    result = (p1 + 5) * 2 - 1  # Should be (beat + 5) * 2 - 1
    
    print(f"Created operation chain: (PointInTime() + 5) * 2 - 1 = {result}")
    
    # Define the base point
    p1.beat = 3
    
    # The result should still be undefined, but we can create a new result
    # by setting the beat on the result object
    result.beat = 10  # This should apply: (10 + 5) * 2 - 1 = 29
    
    print(f"After setting result.beat = 10: {result}")
    assert result.beat == 29
    
    print("✓ Operation application test passed!\n")

def test_mixed_operations():
    """Test operations between defined and undefined PointInTime objects"""
    print("=== Testing Mixed Operations ===")
    
    p_defined = PointInTime(8)
    p_undefined = PointInTime()
    
    # Operation between defined and undefined
    result = p_defined + p_undefined
    print(f"PointInTime(8) + PointInTime() = {result}")
    assert not result.is_defined
    
    # Now define the undefined point
    p_undefined.beat = 4
    # The result should still be undefined because it was created before p_undefined was defined
    
    print("✓ Mixed operations test passed!\n")

def test_error_cases():
    """Test error cases"""
    print("=== Testing Error Cases ===")
    
    p1 = PointInTime(10)
    
    # Test division by zero
    try:
        result = p1 / 0
        assert False, "Should have raised ZeroDivisionError"
    except ZeroDivisionError:
        print("✓ Division by zero correctly raises ZeroDivisionError")
    
    # Test redefining a point
    try:
        p1.beat = 20
        assert False, "Should have raised ValueError"
    except ValueError:
        print("✓ Redefining beat correctly raises ValueError")
    
    # Test unsupported operand types
    try:
        result = p1 + "string"
        assert False, "Should have raised TypeError"
    except TypeError:
        print("✓ Unsupported operand type correctly raises TypeError")
    
    print("✓ All error cases passed!\n")

if __name__ == "__main__":
    print("Testing PointInTime arithmetic operations...\n")
    
    test_defined_arithmetic()
    test_undefined_arithmetic()
    test_operation_application()
    test_mixed_operations()
    test_error_cases()
    
    print("🎉 All tests passed! PointInTime arithmetic operations are working correctly.")