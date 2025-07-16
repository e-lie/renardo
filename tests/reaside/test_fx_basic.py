#!/usr/bin/env python3
"""Test basic FX functionality."""

import pytest


def test_track_fx_count_empty(test_track):
    """Test getting FX count on empty track."""
    fx_count = test_track.get_fx_count()
    assert fx_count == 0, "Empty track should have 0 FX"


def test_add_single_fx(test_track):
    """Test adding a single FX to a track."""
    initial_fx_count = test_track.get_fx_count()
    
    # Add ReaEQ FX
    fx_added = test_track.add_fx("ReaEQ")
    assert fx_added, "Should be able to add ReaEQ"
    
    # Verify FX was added
    new_fx_count = test_track.get_fx_count()
    assert new_fx_count == initial_fx_count + 1, "FX count should increase by 1"


def test_add_fx_reacomp(test_track):
    """Test adding ReaComp FX."""
    initial_fx_count = test_track.get_fx_count()
    
    fx_added = test_track.add_fx("ReaComp")
    assert fx_added, "Should be able to add ReaComp"
    
    new_fx_count = test_track.get_fx_count()
    assert new_fx_count == initial_fx_count + 1, "FX count should increase by 1"


def test_add_fx_readelay(test_track):
    """Test adding ReaDelay FX."""
    initial_fx_count = test_track.get_fx_count()
    
    fx_added = test_track.add_fx("ReaDelay")
    assert fx_added, "Should be able to add ReaDelay"
    
    new_fx_count = test_track.get_fx_count()
    assert new_fx_count == initial_fx_count + 1, "FX count should increase by 1"


def test_add_invalid_fx(test_track):
    """Test adding non-existent FX."""
    initial_fx_count = test_track.get_fx_count()
    
    fx_added = test_track.add_fx("NonExistentFX")
    assert not fx_added, "Should not be able to add non-existent FX"
    
    # FX count should remain the same
    new_fx_count = test_track.get_fx_count()
    assert new_fx_count == initial_fx_count, "FX count should not change"


def test_add_multiple_fx_sequential(test_track):
    """Test adding multiple FX sequentially."""
    fx_list = ["ReaEQ", "ReaComp", "ReaDelay"]
    
    for i, fx_name in enumerate(fx_list):
        fx_added = test_track.add_fx(fx_name)
        assert fx_added, f"Should be able to add {fx_name}"
        
        # Verify FX count
        fx_count = test_track.get_fx_count()
        assert fx_count == i + 1, f"FX count should be {i + 1}"


def test_get_fx_name_first(test_track_with_fx):
    """Test getting name of first FX."""
    fx_name = test_track_with_fx.get_fx_name(0)
    assert isinstance(fx_name, str), "FX name should be a string"
    assert "ReaEQ" in fx_name, f"FX name should contain ReaEQ, got: {fx_name}"


def test_get_fx_name_invalid_index(test_track_with_fx):
    """Test getting FX name with invalid index."""
    fx_count = test_track_with_fx.get_fx_count()
    
    # Test negative index
    fx_name = test_track_with_fx.get_fx_name(-1)
    assert fx_name == "", "Invalid negative index should return empty string"
    
    # Test index too high
    fx_name = test_track_with_fx.get_fx_name(fx_count + 10)
    assert fx_name == "", "Invalid high index should return empty string"


def test_fx_enabled_state(test_track_with_fx):
    """Test getting FX enabled state."""
    is_enabled = test_track_with_fx.is_fx_enabled(0)
    assert isinstance(is_enabled, bool), "FX enabled state should be boolean"


def test_fx_enabled_invalid_index(test_track_with_fx):
    """Test getting FX enabled state with invalid index."""
    fx_count = test_track_with_fx.get_fx_count()
    
    # Test index too high - should return False or handle gracefully
    is_enabled = test_track_with_fx.is_fx_enabled(fx_count + 10)
    assert isinstance(is_enabled, bool), "Should return boolean even for invalid index"


def test_track_fx_count_with_fx(test_track_with_fx):
    """Test getting FX count on track with FX."""
    fx_count = test_track_with_fx.get_fx_count()
    assert fx_count >= 1, "Track with FX should have at least 1 FX"


def test_multiple_fx_names(test_track):
    """Test getting names of multiple FX."""
    fx_list = ["ReaEQ", "ReaComp"]
    
    # Add multiple FX
    for fx_name in fx_list:
        fx_added = test_track.add_fx(fx_name)
        assert fx_added, f"Should be able to add {fx_name}"
    
    # Check names
    for i, expected_fx in enumerate(fx_list):
        fx_name = test_track.get_fx_name(i)
        assert expected_fx.lower() in fx_name.lower(), f"FX name should contain {expected_fx}, got: {fx_name}"


def test_fx_count_consistency(test_track):
    """Test that FX count is consistent after operations."""
    initial_count = test_track.get_fx_count()
    
    # Add FX
    test_track.add_fx("ReaEQ")
    count_after_add = test_track.get_fx_count()
    assert count_after_add == initial_count + 1
    
    # Get FX count multiple times - should be consistent
    for _ in range(3):
        count = test_track.get_fx_count()
        assert count == count_after_add, "FX count should be consistent"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])