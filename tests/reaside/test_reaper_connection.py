#!/usr/bin/env python3
"""Functional test for REAPER connection with reaside."""

import sys
import os
import time
import pytest
from pathlib import Path

# Add src to path to import renardo modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from renardo.reaper_backend.reaside.tools.reaper_program import start_reaper, stop_reaper, is_reaper_running
from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
from renardo.reaper_backend.reaside.core.reaper import Reaper
from renardo.reaper_backend.reaside.core.project import Project
from renardo.reaper_backend.reaside.core.track import Track
from renardo.reaper_backend.reaside import configure_reaper


# Module-level variables for REAPER session
_reaper_started = False
_reaper_process = None
_client = None
_reaper = None


@pytest.fixture(scope="session")
def reaper_session():
    """Start REAPER once for the entire test session."""
    global _reaper_started, _reaper_process, _client, _reaper
    
    print("Setting up REAPER for tests...")
    
    # Configure REAPER (install Lua scripts)
    try:
        configure_reaper()
        print("REAPER configured successfully")
    except Exception as e:
        print(f"REAPER configuration failed: {e}")
        # Continue anyway, configuration might already be done
    
    # Start REAPER
    print("Starting REAPER...")
    success, python_home, process = start_reaper(detached=True)
    
    if success:
        print(f"REAPER started successfully (Python home: {python_home})")
        _reaper_started = True
        _reaper_process = process
        
        # Wait for REAPER to be ready
        print("Waiting for REAPER to be ready...")
        time.sleep(8)  # Give more time for startup
        
        # Initialize client with default parameters
        _client = ReaperClient()
        
        # Create Reaper instance
        _reaper = Reaper(_client)
        
    else:
        pytest.fail("Failed to start REAPER")
    
    yield _reaper
    
    # Cleanup after all tests
    if _client:
        # Stop OSC server if running
        try:
            _client.stop_osc_server()
        except:
            pass
    
    if _reaper_started:
        print("Stopping REAPER...")
        success = stop_reaper()
        if success:
            print("REAPER stopped successfully")
        else:
            print("Failed to stop REAPER cleanly")
            
        # Wait for shutdown
        time.sleep(3)
        
        # Verify REAPER is stopped
        if is_reaper_running():
            print("Warning: REAPER might still be running")


@pytest.fixture
def client(reaper_session):
    """Get connected client for each test."""
    # Verify REAPER is accessible
    connected = reaper_session._client.ping()
    assert connected, "Failed to connect to REAPER"
    
    yield reaper_session._client


@pytest.fixture
def project(reaper_session):
    """Get project instance for each test."""
    # Get current project (index 0)
    return reaper_session.current_project


def test_reaper_connection(client):
    """Test basic REAPER connection."""
    # Test getting REAPER version
    version = client.get_reaper_version()
    assert version is not None, "Could not get REAPER version"
    print(f"REAPER version: {version}")


def test_project_operations(project):
    """Test basic project operations."""
    # Test getting project name
    original_name = project.name
    assert original_name is not None, "Could not get project name"
    
    # Test setting project name
    test_name = "Test Project"
    project.name = test_name
    new_name = project.name
    assert new_name == test_name, "Project name was not set correctly"
    
    # Test getting track count
    track_count = len(project.tracks)
    assert isinstance(track_count, int), "Track count should be an integer"
    assert track_count >= 0, "Track count should be non-negative"
    
    print(f"Original project name: {original_name}")
    print(f"New project name: {new_name}")
    print(f"Track count: {track_count}")


def test_track_operations(project, client):
    """Test basic track operations."""
    # Add a new track
    track = project.add_track()
    assert track is not None, "Should be able to add a track"
    
    # Test setting track name
    test_track_name = "Test Track"
    track.name = test_track_name
    track_name = track.name
    assert track_name == test_track_name, "Track name was not set correctly"
    
    # Test track volume
    test_volume = -6.0
    track.volume = test_volume
    volume = track.volume
    assert pytest.approx(volume, abs=1.0) == test_volume, "Track volume was not set correctly"
    
    # Test track mute
    track.is_muted = True
    is_muted = track.is_muted
    assert is_muted, "Track should be muted"
    
    track.is_muted = False
    is_muted = track.is_muted
    assert not is_muted, "Track should not be muted"
    
    print(f"Added track at index: {track.index}")
    print(f"Track name: {track_name}")
    print(f"Track volume: {volume} dB")
    print(f"Track mute test passed")


def test_track_listing(project, client):
    """Test listing tracks."""
    # Add multiple tracks
    added_tracks = []
    for i in range(3):
        track = project.add_track()
        added_tracks.append(track)
        
        # Set track name
        track.name = f"Track {i+1}"
    
    # Get track count
    track_count = len(project.tracks)
    assert track_count >= len(added_tracks), "Track count should include newly added tracks"
    
    # List all tracks
    tracks = project.tracks
    assert isinstance(tracks, list), "Tracks should be a list"
    assert len(tracks) >= len(added_tracks), "Should have at least the tracks we added"
    
    print(f"Added {len(added_tracks)} tracks")
    print(f"Total track count: {track_count}")
    print(f"Tracks list length: {len(tracks)}")
    
    # Test track access by index
    for i, track in enumerate(added_tracks):
        assert track is not None, f"Should be able to get track {track.index}"
        
        track_name = track.name
        expected_name = f"Track {i+1}"
        assert track_name == expected_name, f"Track name should be '{expected_name}', got '{track_name}'"
        
        print(f"Track {track.index}: {track_name}")


def test_fx_operations(project, client):
    """Test basic FX operations."""
    # Add a track for FX testing
    track = project.add_track()
    track.name = "FX Test Track"
    
    # NOTE: FX operations would need to be implemented in the track class
    # For now, just test that the track was created
    assert track is not None, "Should be able to add a track"
    assert track.name == "FX Test Track", "Track name should be set correctly"
    
    print(f"Added FX test track at index: {track.index}")
    print(f"Track name: {track.name}")
    
    # TODO: Add FX operations tests when implemented
    # fx_added = track.add_fx("ReaEQ")
    # assert fx_added, "Should be able to add ReaEQ"


if __name__ == '__main__':
    # Run with pytest
    pytest.main([__file__, '-v'])