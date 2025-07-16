#!/usr/bin/env python3
"""Test REAPER startup and connection functionality."""

import pytest
import time


def test_reaper_is_running(reaper_session):
    """Test that REAPER is running and accessible."""
    assert reaper_session is not None, "REAPER session should be available"


def test_client_connection(client):
    """Test that client can connect to REAPER."""
    connected = client.ping()
    assert connected, "Client should be able to ping REAPER"


def test_client_reconnection(client):
    """Test that client can reconnect after disconnection."""
    # First connection
    connected = client.ping()
    assert connected, "Initial connection should work"
    
    # Simulate reconnection
    time.sleep(0.1)
    connected = client.ping()
    assert connected, "Reconnection should work"


def test_reaper_version_info(client):
    """Test retrieving REAPER version information."""
    try:
        version = client.call_reascript_function("GetAppVersion")
        assert version is not None, "Should be able to get REAPER version"
        assert len(str(version)) > 0, "Version should not be empty"
        print(f"REAPER version: {version}")
    except Exception as e:
        pytest.fail(f"Failed to get REAPER version: {e}")


def test_reaper_main_window(client):
    """Test that REAPER main window is accessible."""
    try:
        # Try to get main window handle
        main_window = client.call_reascript_function("GetMainHwnd")
        assert main_window is not None, "Should be able to get main window"
    except Exception as e:
        pytest.fail(f"Failed to get main window: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])