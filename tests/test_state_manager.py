"""
Tests for the StateManager class
"""
import pytest
from datetime import datetime
from renardo.renardo_app.state_manager import StateManager


@pytest.fixture
def state_manager():
    """Create a fresh StateManager instance for each test"""
    return StateManager()


def test_get_state(state_manager):
    """Test get_state returns the entire state"""
    state = state_manager.get_state()
    assert isinstance(state, dict)
    assert "counter" in state
    assert "renardo_init" in state
    assert "log_messages" in state


def test_increment_counter(state_manager):
    """Test increment_counter increments the counter value"""
    initial_counter = state_manager._state["counter"]
    new_counter = state_manager.increment_counter()
    assert new_counter == initial_counter + 1
    assert state_manager._state["counter"] == new_counter


def test_update_state(state_manager):
    """Test update_state updates a specific key in the state"""
    state_manager.update_state("welcome_text", "Updated text")
    assert state_manager._state["welcome_text"] == "Updated text"
    
    # Test with a non-existent key (should not change state)
    original_state = state_manager._state.copy()
    state_manager.update_state("non_existent_key", "value")
    assert state_manager._state == original_state


def test_get_renardo_status(state_manager):
    """Test get_renardo_status returns the renardo_init section"""
    status = state_manager.get_renardo_status()
    assert "superColliderClasses" in status
    assert "samples" in status
    assert "instruments" in status


def test_update_renardo_init_status(state_manager):
    """Test update_renardo_init_status updates a component status"""
    # Set samples to True
    state_manager.update_renardo_init_status("samples", True)
    assert state_manager._state["renardo_init"]["samples"] is True
    
    # Set samples back to False
    state_manager.update_renardo_init_status("samples", False)
    assert state_manager._state["renardo_init"]["samples"] is False
    
    # Test with a non-existent component (should not change state)
    original_state = state_manager._state["renardo_init"].copy()
    state_manager.update_renardo_init_status("non_existent", True)
    assert state_manager._state["renardo_init"] == original_state


def test_add_log_message(state_manager):
    """Test add_log_message adds a log message"""
    # Clear any existing log messages
    state_manager._state["log_messages"] = []
    
    # Add a log message
    log_entry = state_manager.add_log_message("Test message")
    
    # Verify the log entry
    assert log_entry["message"] == "Test message"
    assert log_entry["level"] == "INFO"
    assert "timestamp" in log_entry
    
    # Verify the log message was added to the state
    assert len(state_manager._state["log_messages"]) == 1
    assert state_manager._state["log_messages"][0] == log_entry
    
    # Test with a custom level
    log_entry = state_manager.add_log_message("Error message", "ERROR")
    assert log_entry["level"] == "ERROR"


def test_max_log_messages(state_manager):
    """Test that only the 1000 most recent log messages are kept"""
    # Clear existing log messages
    state_manager._state["log_messages"] = []
    
    # Add 1100 log messages
    for i in range(1100):
        state_manager.add_log_message(f"Message {i}")
    
    # Verify only 1000 messages are kept
    assert len(state_manager._state["log_messages"]) == 1000
    
    # Verify the oldest messages were removed
    first_message = state_manager._state["log_messages"][0]
    assert first_message["message"] == "Message 100"


def test_get_log_messages(state_manager):
    """Test get_log_messages returns all log messages"""
    # Clear existing log messages
    state_manager._state["log_messages"] = []
    
    # Add some log messages
    state_manager.add_log_message("Message 1")
    state_manager.add_log_message("Message 2")
    
    # Verify get_log_messages returns all messages
    log_messages = state_manager.get_log_messages()
    assert len(log_messages) == 2
    assert log_messages[0]["message"] == "Message 1"
    assert log_messages[1]["message"] == "Message 2"


def test_reset_state(state_manager):
    """Test reset_state resets the state to default values"""
    # Modify the state
    state_manager._state["counter"] = 10
    state_manager._state["renardo_init"]["samples"] = True
    state_manager.add_log_message("Test message")
    
    # Reset the state
    state_manager.reset_state()
    
    # Verify the state was reset
    assert state_manager._state["counter"] == 0
    assert state_manager._state["renardo_init"]["samples"] is False
    assert state_manager._state["log_messages"] == []