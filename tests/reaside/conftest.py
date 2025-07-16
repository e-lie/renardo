#!/usr/bin/env python3
"""Shared fixtures for reaside tests."""

import sys
import os
import time
import pytest
import tempfile
from pathlib import Path

# Add src to path to import renardo modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from renardo.reaper_backend.reaside.tools.reaper_program import start_reaper, stop_reaper, is_reaper_running
from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
from renardo.reaper_backend.reaside.core.reaper import Reaper
from renardo.reaper_backend.reaside.core.project import Project
from renardo.reaper_backend.reaside.core.track import Track
from renardo.reaper_backend.reaside.core.fx import ReaFX
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
    
    print("Setting up REAPER for test session...")
    
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
def reaper_instance(reaper_session):
    """Get Reaper instance for each test."""
    yield reaper_session


@pytest.fixture
def project(reaper_session):
    """Get project instance for each test."""
    # Get current project (index 0)
    return reaper_session.current_project


@pytest.fixture
def clean_project(project):
    """Get a clean project with no extra tracks."""
    # Remove all tracks except master
    track_count = project._client.call_reascript_function("CountTracks", project._index)
    for i in range(track_count - 1, 0, -1):  # Skip master track (index 0)
        try:
            track = project.get_track(i)
            track.delete()
        except:
            pass
    
    yield project


@pytest.fixture
def test_track(clean_project):
    """Create a test track for each test."""
    track = clean_project.add_track()
    track.name = "Test Track"
    yield track


@pytest.fixture
def test_track_with_fx(test_track):
    """Create a test track with a ReaEQ FX."""
    success = test_track.add_fx("ReaEQ")
    assert success, "Failed to add ReaEQ to test track"
    yield test_track


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def fx_chain_file(temp_dir):
    """Create a temporary FX chain file path."""
    yield temp_dir / "test_fx_chain.RfxChain"


@pytest.fixture
def reafx_instance(client, test_track_with_fx):
    """Create a ReaFX instance for testing."""
    fx = ReaFX(client, test_track_with_fx.index, 0, "ReaEQ")
    yield fx