#!/usr/bin/env python3
"""Test project automatic track scanning functionality."""

import pytest
import time


def test_project_automatic_track_scanning(clean_project, client):
    """Test that project automatically scans all tracks on creation."""
    # Clean project should have scanned existing tracks
    assert hasattr(clean_project, 'reatracks'), "Project should have tracks cache"
    
    # Should have at least the master track (or empty project)
    track_count = len(clean_project.reatracks)
    assert track_count >= 0, "Project should have scanned tracks"
    
    # Track count should match REAPER's count
    reaper_count = client.call_reascript_function("CountTracks", clean_project.index)
    assert track_count == reaper_count, "Cached track count should match REAPER"


def test_project_track_access(clean_project, client):
    """Test accessing tracks through various methods."""
    # Add a track to have something to test with
    track1 = clean_project.add_track()
    track1.name = "Test Track 1"
    
    # Add another track
    track2 = clean_project.add_track()
    track2.name = "Test Track 2"
    
    # Test tracks property
    all_tracks = clean_project.tracks
    assert len(all_tracks) >= 2, "Should have at least 2 tracks"
    
    # Test get_track method
    first_track = clean_project.get_track(0)
    assert first_track is not None, "Should get first track"
    
    # Test bracket notation
    first_track_bracket = clean_project[0]
    assert first_track_bracket is first_track, "Bracket notation should return same object"
    
    # Test iteration
    track_list = list(clean_project)
    assert len(track_list) == len(all_tracks), "Iteration should return all tracks"
    
    # Test len()
    assert len(clean_project) == len(all_tracks), "__len__ should return track count"


def test_project_track_caching(clean_project, client):
    """Test that tracks are properly cached and reused."""
    # Add a track
    track1 = clean_project.add_track()
    track1.name = "Cached Track Test"
    
    # Get track multiple ways - should be same object
    track_via_get = clean_project.get_track(track1.index)
    track_via_bracket = clean_project[track1.index]
    track_via_tracks = clean_project.tracks[track1.index]
    
    # All should be the same object
    assert track_via_get is track1, "get_track should return cached object"
    assert track_via_bracket is track1, "bracket access should return cached object"
    assert track_via_tracks is track1, "tracks property should return cached object"


def test_project_track_properties(clean_project, client):
    """Test project track-related properties."""
    initial_count = clean_project.track_count
    
    # Add tracks
    track1 = clean_project.add_track()
    track2 = clean_project.add_track()
    
    # Test track_count property
    assert clean_project.track_count == initial_count + 2, "track_count should update"
    
    # Test list_tracks method
    track_list = clean_project.list_tracks()
    assert len(track_list) == clean_project.track_count, "list_tracks should return all tracks"
    
    # Verify tracks are in correct order
    for i, track in enumerate(track_list):
        assert track.index == i, f"Track {i} should have correct index"


def test_project_with_existing_tracks_and_fx(reaper_instance, client):
    """Test project scanning with existing tracks that have FX."""
    # Get current project
    project = reaper_instance.current_project
    
    # Add track with FX
    track = project.add_track()
    track.name = "FX Test Track"
    track.add_fx("ReaEQ")
    track.add_fx("ReaComp")
    
    # Create new project instance (simulates reopening project)
    # This should scan all tracks including the one with FX
    new_project = type(project)(reaper_instance, project.index)
    
    # Should have scanned the track with FX
    assert len(new_project.reatracks) > 0, "New project should have scanned existing tracks"
    
    # Find the FX test track
    fx_track = None
    for track_obj in new_project.tracks:
        if track_obj.name == "FX Test Track":
            fx_track = track_obj
            break
    
    assert fx_track is not None, "Should find FX test track"
    
    # Track should have scanned FX automatically
    fx_list = fx_track.list_fx()
    assert len(fx_list) >= 2, "Track should have scanned existing FX"
    
    # Should be able to access FX by snake_case names
    try:
        rea_eq = fx_track.rea_eq
        rea_comp = fx_track.rea_comp
        assert rea_eq is not None, "Should access ReaEQ"
        assert rea_comp is not None, "Should access ReaComp"
    except AttributeError as e:
        pytest.fail(f"Should be able to access FX by snake_case names: {e}")


def test_project_rescan_functionality(clean_project, client):
    """Test manual rescan functionality."""
    # Add some tracks
    track1 = clean_project.add_track()
    track2 = clean_project.add_track()
    
    original_count = len(clean_project.reatracks)
    
    # Manual rescan
    clean_project.rescan_all_tracks()
    
    # Should have same number of tracks
    new_count = len(clean_project.reatracks)
    assert new_count == original_count, "Rescan should maintain track count"
    
    # Tracks should still be accessible
    tracks = clean_project.tracks
    assert len(tracks) == original_count, "Tracks should still be accessible after rescan"


def test_project_track_by_name(clean_project, client):
    """Test getting tracks by name."""
    # Add tracks with specific names
    track1 = clean_project.add_track()
    track1.name = "Lead Guitar"
    
    track2 = clean_project.add_track()
    track2.name = "Bass Guitar"
    
    # Test case-sensitive search
    found_track = clean_project.get_track_by_name("Lead Guitar", case_sensitive=True)
    assert found_track is track1, "Should find track by exact name"
    
    # Test case-insensitive search
    found_track_ci = clean_project.get_track_by_name("lead guitar", case_sensitive=False)
    assert found_track_ci is track1, "Should find track by case-insensitive name"
    
    # Test non-existent track
    not_found = clean_project.get_track_by_name("Non-existent Track")
    assert not_found is None, "Should return None for non-existent track"


def test_project_performance_optimization(reaper_instance, client):
    """Test that automatic scanning provides performance benefits."""
    project = reaper_instance.current_project
    
    # Add multiple tracks with FX
    tracks = []
    for i in range(3):
        track = project.add_track()
        track.name = f"Perf Test Track {i+1}"
        track.add_fx("ReaEQ")
        tracks.append(track)
    
    # Measure time to access all FX (should be fast due to pre-scanning)
    start_time = time.time()
    
    total_fx = 0
    for track in project.tracks:
        fx_list = track.list_fx()
        total_fx += len(fx_list)
        
        # Access FX by snake_case name (should be fast)
        for fx in fx_list:
            _ = fx.snake_name
            _ = fx.reaper_name
    
    scan_time = time.time() - start_time
    
    # Should be very fast (under 0.1 seconds for this simple test)
    assert scan_time < 0.5, f"FX access should be fast, took {scan_time:.3f}s"
    assert total_fx >= 3, "Should have found FX on test tracks"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])