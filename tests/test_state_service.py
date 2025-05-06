"""
Tests for the state_service module to ensure it correctly delegates to StateManager
"""
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_state_manager():
    """Create a mock state manager and app for testing"""
    mock_app = MagicMock()
    mock_sm = MagicMock()
    mock_app.state_manager = mock_sm
    return mock_app, mock_sm


@patch('renardo.webserver.state_service._get_state_manager')
def test_get_state(mock_get_state_manager):
    """Test that get_state delegates to StateManager"""
    # Set up mock
    mock_sm = MagicMock()
    mock_sm.get_state.return_value = {"counter": 0}
    mock_get_state_manager.return_value = mock_sm
    
    # Import here to ensure patching works
    from renardo.webserver import state_service
    
    # Test get_state
    result = state_service.get_state()
    
    # Verify behavior
    mock_sm.get_state.assert_called_once()
    assert result == {"counter": 0}


@patch('renardo.webserver.state_service._get_state_manager')
def test_increment_counter(mock_get_state_manager):
    """Test that increment_counter delegates to StateManager"""
    # Set up mock
    mock_sm = MagicMock()
    mock_sm.increment_counter.return_value = 1
    mock_get_state_manager.return_value = mock_sm
    
    # Import here to ensure patching works
    from renardo.webserver import state_service
    
    # Test increment_counter
    result = state_service.increment_counter()
    
    # Verify behavior
    mock_sm.increment_counter.assert_called_once()
    assert result == 1


@patch('renardo.webserver.state_service._get_state_manager')
def test_update_state(mock_get_state_manager):
    """Test that update_state delegates to StateManager"""
    # Set up mock
    mock_sm = MagicMock()
    mock_sm.update_state.return_value = {"counter": 5}
    mock_get_state_manager.return_value = mock_sm
    
    # Import here to ensure patching works
    from renardo.webserver import state_service
    
    # Test update_state
    result = state_service.update_state("counter", 5)
    
    # Verify behavior
    mock_sm.update_state.assert_called_once_with("counter", 5)
    assert result == {"counter": 5}


@patch('renardo.webserver.state_service._get_state_manager')
def test_get_renardo_status(mock_get_state_manager):
    """Test that get_renardo_status delegates to StateManager"""
    # Set up mock
    mock_sm = MagicMock()
    mock_sm.get_renardo_status.return_value = {"samples": True}
    mock_get_state_manager.return_value = mock_sm
    
    # Import here to ensure patching works
    from renardo.webserver import state_service
    
    # Test get_renardo_status
    result = state_service.get_renardo_status()
    
    # Verify behavior
    mock_sm.get_renardo_status.assert_called_once()
    assert result == {"samples": True}


@patch('renardo.webserver.state_service._get_state_manager')
def test_update_renardo_init_status(mock_get_state_manager):
    """Test that update_renardo_init_status delegates to StateManager"""
    # Set up mock
    mock_sm = MagicMock()
    mock_sm.update_renardo_init_status.return_value = {"samples": True}
    mock_get_state_manager.return_value = mock_sm
    
    # Import here to ensure patching works
    from renardo.webserver import state_service
    
    # Test update_renardo_init_status
    result = state_service.update_renardo_init_status("samples", True)
    
    # Verify behavior
    mock_sm.update_renardo_init_status.assert_called_once_with("samples", True)
    assert result == {"samples": True}


@patch('renardo.webserver.state_service._get_state_manager')
def test_add_log_message(mock_get_state_manager):
    """Test that add_log_message delegates to StateManager"""
    # Set up mock
    mock_sm = MagicMock()
    expected_log = {"timestamp": "12:00:00", "level": "INFO", "message": "Test"}
    mock_sm.add_log_message.return_value = expected_log
    mock_get_state_manager.return_value = mock_sm
    
    # Import here to ensure patching works
    from renardo.webserver import state_service
    
    # Test add_log_message
    result = state_service.add_log_message("Test")
    
    # Verify behavior
    mock_sm.add_log_message.assert_called_once_with("Test", "INFO")
    assert result == expected_log


@patch('renardo.webserver.state_service._get_state_manager')
def test_reset_state(mock_get_state_manager):
    """Test that reset_state delegates to StateManager"""
    # Set up mock
    mock_sm = MagicMock()
    mock_sm.reset_state.return_value = {"counter": 0}
    mock_get_state_manager.return_value = mock_sm
    
    # Import here to ensure patching works
    from renardo.webserver import state_service
    
    # Test reset_state
    result = state_service.reset_state()
    
    # Verify behavior
    mock_sm.reset_state.assert_called_once()
    assert result == {"counter": 0}