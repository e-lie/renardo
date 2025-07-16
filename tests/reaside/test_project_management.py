#!/usr/bin/env python3
"""Test REAPER project management functionality."""

import pytest


def test_project_access(project):
    """Test that project is accessible."""
    assert project is not None, "Project should be available"


def test_project_name_get(project):
    """Test getting project name."""
    name = project.name
    assert isinstance(name, str), "Project name should be a string"
    print(f"Project name: '{name}'")


def test_project_name_set(project):
    """Test setting project name."""
    original_name = project.name
    test_name = "Test Project Name"
    
    # Set new name
    project.name = test_name
    
    # Verify name was set
    current_name = project.name
    assert current_name == test_name, f"Project name should be '{test_name}', got '{current_name}'"
    
    # Restore original name
    project.name = original_name


def test_project_name_empty_string(project):
    """Test setting project name to empty string."""
    original_name = project.name
    
    # Set empty name
    project.name = ""
    
    # Verify name was set (empty string should be valid)
    current_name = project.name
    assert current_name == "", f"Project name should be empty, got '{current_name}'"
    
    # Restore original name
    project.name = original_name


def test_project_name_special_characters(project):
    """Test setting project name with special characters."""
    original_name = project.name
    test_name = "Test-Project_Name (2024) [v1.0]"
    
    # Set new name with special characters
    project.name = test_name
    
    # Verify name was set
    current_name = project.name
    assert current_name == test_name, f"Project name should be '{test_name}', got '{current_name}'"
    
    # Restore original name
    project.name = original_name


def test_project_track_count(project):
    """Test getting project track count."""
    track_count = project._client.call_reascript_function("CountTracks", project._index)
    assert isinstance(track_count, int), "Track count should be an integer"
    assert track_count >= 1, "Project should have at least master track"
    print(f"Track count: {track_count}")


def test_project_master_track(project):
    """Test accessing master track."""
    master_track = project.get_track(0)
    assert master_track is not None, "Master track should exist"
    assert master_track.index == 0, "Master track should have index 0"


def test_project_track_access_bounds(project):
    """Test accessing tracks with invalid indices."""
    track_count = project._client.call_reascript_function("CountTracks", project._index)
    
    # Test negative index
    with pytest.raises((IndexError, ValueError)):
        project.get_track(-1)
    
    # Test index too high
    with pytest.raises((IndexError, ValueError)):
        project.get_track(track_count + 10)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])