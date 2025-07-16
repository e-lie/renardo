#!/usr/bin/env python3
"""Test basic track functionality."""

import pytest


def test_track_creation(clean_project):
    """Test creating a new track."""
    initial_count = clean_project._client.call_reascript_function("CountTracks", clean_project._index)
    
    # Add a track
    track = clean_project.add_track()
    assert track is not None, "Track should be created"
    
    # Verify track count increased
    new_count = clean_project._client.call_reascript_function("CountTracks", clean_project._index)
    assert new_count == initial_count + 1, "Track count should increase by 1"
    
    # Verify track has correct index
    assert track.index == initial_count, f"Track index should be {initial_count}"


def test_track_name_get(test_track):
    """Test getting track name."""
    name = test_track.name
    assert isinstance(name, str), "Track name should be a string"
    print(f"Track name: '{name}'")


def test_track_name_set(test_track):
    """Test setting track name."""
    original_name = test_track.name
    test_name = "My Test Track"
    
    # Set new name
    test_track.name = test_name
    
    # Verify name was set
    current_name = test_track.name
    assert current_name == test_name, f"Track name should be '{test_name}', got '{current_name}'"




def test_track_selection_get(test_track):
    """Test getting track selection state."""
    is_selected = test_track.is_selected
    assert isinstance(is_selected, bool), "Selection state should be boolean"


def test_track_selection_set(test_track):
    """Test setting track selection state."""
    # Set selected
    test_track.is_selected = True
    assert test_track.is_selected == True, "Track should be selected"
    
    # Set unselected
    test_track.is_selected = False
    assert test_track.is_selected == False, "Track should be unselected"


def test_track_mute_get(test_track):
    """Test getting track mute state."""
    is_muted = test_track.is_muted
    assert isinstance(is_muted, bool), "Mute state should be boolean"


def test_track_mute_set(test_track):
    """Test setting track mute state."""
    # Set muted
    test_track.is_muted = True
    assert test_track.is_muted == True, "Track should be muted"
    
    # Set unmuted
    test_track.is_muted = False
    assert test_track.is_muted == False, "Track should be unmuted"


def test_track_solo_get(test_track):
    """Test getting track solo state."""
    is_soloed = test_track.is_soloed
    assert isinstance(is_soloed, bool), "Solo state should be boolean"


def test_track_solo_set(test_track):
    """Test setting track solo state."""
    # Set soloed
    test_track.is_soloed = True
    assert test_track.is_soloed == True, "Track should be soloed"
    
    # Set unsoloed
    test_track.is_soloed = False
    assert test_track.is_soloed == False, "Track should be unsoloed"


def test_track_volume_get(test_track):
    """Test getting track volume."""
    volume = test_track.volume
    assert isinstance(volume, (int, float)), "Volume should be numeric"
    assert volume >= 0, "Volume should be non-negative"


def test_track_volume_set(test_track):
    """Test setting track volume."""
    original_volume = test_track.volume
    test_volume = 0.5
    
    # Set volume
    test_track.volume = test_volume
    
    # Verify volume was set (allow small floating point differences)
    current_volume = test_track.volume
    assert abs(current_volume - test_volume) < 0.01, f"Volume should be {test_volume}, got {current_volume}"


def test_track_pan_get(test_track):
    """Test getting track pan."""
    pan = test_track.pan
    assert isinstance(pan, (int, float)), "Pan should be numeric"
    assert -1.0 <= pan <= 1.0, "Pan should be between -1.0 and 1.0"


def test_track_pan_set(test_track):
    """Test setting track pan."""
    original_pan = test_track.pan
    test_pan = 0.25
    
    # Set pan
    test_track.pan = test_pan
    
    # Verify pan was set (allow small floating point differences)
    current_pan = test_track.pan
    assert abs(current_pan - test_pan) < 0.01, f"Pan should be {test_pan}, got {current_pan}"


def test_track_deletion(clean_project):
    """Test deleting a track."""
    initial_count = clean_project._client.call_reascript_function("CountTracks", clean_project._index)
    
    # Add a track
    track = clean_project.add_track()
    assert clean_project._client.call_reascript_function("CountTracks", clean_project._index) == initial_count + 1
    
    # Delete the track
    result = track.delete()
    assert result, "Track deletion should succeed"
    
    # Verify track count decreased
    final_count = clean_project._client.call_reascript_function("CountTracks", clean_project._index)
    assert final_count == initial_count, "Track count should return to initial value"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])