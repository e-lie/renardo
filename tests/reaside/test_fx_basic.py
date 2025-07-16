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


def test_add_multiple_fx(test_track):
    """Test adding multiple FX sequentially."""
    fx_list = ["ReaEQ", "ReaComp"]
    
    for i, fx_name in enumerate(fx_list):
        fx_added = test_track.add_fx(fx_name)
        assert fx_added, f"Should be able to add {fx_name}"
        
        # Verify FX count
        fx_count = test_track.get_fx_count()
        assert fx_count == i + 1, f"FX count should be {i + 1}"


def test_get_fx_name(test_track_with_fx):
    """Test getting name of FX."""
    fx_name = test_track_with_fx.get_fx_name(0)
    assert isinstance(fx_name, str), "FX name should be a string"
    assert "ReaEQ" in fx_name, f"FX name should contain ReaEQ, got: {fx_name}"


def test_fx_enabled_state(test_track_with_fx):
    """Test getting FX enabled state."""
    is_enabled = test_track_with_fx.is_fx_enabled(0)
    assert isinstance(is_enabled, bool), "FX enabled state should be boolean"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])