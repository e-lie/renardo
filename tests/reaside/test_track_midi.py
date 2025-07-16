#!/usr/bin/env python3
"""Test track MIDI functionality."""

import pytest
import time
import threading


def test_send_note_on(test_track):
    """Test sending MIDI note on."""
    # Test basic note on
    result = test_track.send_note_on(60, 100, 0)
    assert isinstance(result, bool), "send_note_on should return boolean"


def test_send_note_on_parameters(test_track):
    """Test send_note_on with different parameters."""
    # Test with different pitches
    for pitch in [60, 64, 67]:  # C, E, G
        result = test_track.send_note_on(pitch, 100, 0)
        assert isinstance(result, bool), f"send_note_on should work with pitch {pitch}"


def test_send_note_on_velocity(test_track):
    """Test send_note_on with different velocities."""
    # Test with different velocities
    for velocity in [50, 100, 127]:
        result = test_track.send_note_on(60, velocity, 0)
        assert isinstance(result, bool), f"send_note_on should work with velocity {velocity}"


def test_send_note_on_channel(test_track):
    """Test send_note_on with different channels."""
    # Test with different channels
    for channel in [0, 1, 2]:
        result = test_track.send_note_on(60, 100, channel)
        assert isinstance(result, bool), f"send_note_on should work with channel {channel}"


def test_send_note_off(test_track):
    """Test sending MIDI note off."""
    # Send note on first
    test_track.send_note_on(60, 100, 0)
    
    # Send note off
    result = test_track.send_note_off(60, 0)
    assert isinstance(result, bool), "send_note_off should return boolean"


def test_send_note_off_parameters(test_track):
    """Test send_note_off with different parameters."""
    # Test with different pitches
    for pitch in [60, 64, 67]:
        test_track.send_note_on(pitch, 100, 0)
        result = test_track.send_note_off(pitch, 0)
        assert isinstance(result, bool), f"send_note_off should work with pitch {pitch}"


def test_send_note_off_channel(test_track):
    """Test send_note_off with different channels."""
    # Test with different channels
    for channel in [0, 1, 2]:
        test_track.send_note_on(60, 100, channel)
        result = test_track.send_note_off(60, channel)
        assert isinstance(result, bool), f"send_note_off should work with channel {channel}"


def test_send_all_notes_off(test_track):
    """Test sending all notes off."""
    # Send multiple notes on
    test_track.send_note_on(60, 100, 0)
    test_track.send_note_on(64, 100, 0)
    test_track.send_note_on(67, 100, 0)
    
    # Send all notes off
    result = test_track.send_all_notes_off()
    assert isinstance(result, bool), "send_all_notes_off should return boolean"


def test_play_note_basic(test_track):
    """Test playing note with duration."""
    # Test basic note play
    timer = test_track.play_note(60, 100, 0.1, 0)
    assert isinstance(timer, threading.Timer), "play_note should return Timer"
    
    # Wait for note to finish
    timer.join()


def test_play_note_parameters(test_track):
    """Test play_note with different parameters."""
    # Test with different parameters
    timer = test_track.play_note(64, 80, 0.05, 1)
    assert isinstance(timer, threading.Timer), "play_note should return Timer"
    
    # Wait for note to finish
    timer.join()


def test_play_note_duration(test_track):
    """Test play_note duration timing."""
    start_time = time.time()
    duration = 0.1
    
    timer = test_track.play_note(60, 100, duration, 0)
    timer.join()  # Wait for completion
    
    elapsed = time.time() - start_time
    # Allow some tolerance for timing
    assert elapsed >= duration - 0.05, f"Note should play for at least {duration} seconds"
    assert elapsed <= duration + 0.1, f"Note should not play much longer than {duration} seconds"


def test_play_multiple_notes(test_track):
    """Test playing multiple notes simultaneously."""
    timers = []
    
    # Start multiple notes
    for pitch in [60, 64, 67]:
        timer = test_track.play_note(pitch, 100, 0.1, 0)
        timers.append(timer)
    
    # Wait for all notes to finish
    for timer in timers:
        timer.join()


def test_play_note_overlapping(test_track):
    """Test playing overlapping notes."""
    # Start first note
    timer1 = test_track.play_note(60, 100, 0.2, 0)
    
    # Start second note while first is playing
    time.sleep(0.05)
    timer2 = test_track.play_note(64, 100, 0.2, 0)
    
    # Wait for both to finish
    timer1.join()
    timer2.join()


def test_midi_note_range(test_track):
    """Test MIDI notes in different ranges."""
    # Test low notes
    result = test_track.send_note_on(24, 100, 0)  # C1
    assert isinstance(result, bool), "Should handle low notes"
    test_track.send_note_off(24, 0)
    
    # Test high notes
    result = test_track.send_note_on(108, 100, 0)  # C8
    assert isinstance(result, bool), "Should handle high notes"
    test_track.send_note_off(108, 0)


def test_midi_velocity_range(test_track):
    """Test MIDI velocity range."""
    # Test minimum velocity
    result = test_track.send_note_on(60, 1, 0)
    assert isinstance(result, bool), "Should handle minimum velocity"
    test_track.send_note_off(60, 0)
    
    # Test maximum velocity
    result = test_track.send_note_on(60, 127, 0)
    assert isinstance(result, bool), "Should handle maximum velocity"
    test_track.send_note_off(60, 0)


def test_midi_channel_range(test_track):
    """Test MIDI channel range."""
    # Test different channels
    for channel in range(16):  # MIDI channels 0-15
        result = test_track.send_note_on(60, 100, channel)
        assert isinstance(result, bool), f"Should handle channel {channel}"
        test_track.send_note_off(60, channel)


def test_note_on_off_sequence(test_track):
    """Test proper note on/off sequence."""
    pitch = 60
    velocity = 100
    channel = 0
    
    # Send note on
    on_result = test_track.send_note_on(pitch, velocity, channel)
    assert isinstance(on_result, bool), "Note on should return boolean"
    
    # Brief pause
    time.sleep(0.01)
    
    # Send note off
    off_result = test_track.send_note_off(pitch, channel)
    assert isinstance(off_result, bool), "Note off should return boolean"


def test_multiple_tracks_midi(clean_project):
    """Test MIDI on multiple tracks."""
    # Create two tracks
    track1 = clean_project.add_track()
    track2 = clean_project.add_track()
    
    # Send notes to both tracks
    result1 = track1.send_note_on(60, 100, 0)
    result2 = track2.send_note_on(64, 100, 0)
    
    assert isinstance(result1, bool), "First track should handle MIDI"
    assert isinstance(result2, bool), "Second track should handle MIDI"
    
    # Turn off notes
    track1.send_note_off(60, 0)
    track2.send_note_off(64, 0)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])