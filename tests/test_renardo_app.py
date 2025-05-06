"""
Tests for the RenardoApp singleton class
"""
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the singleton instance before each test"""
    # Import here to avoid loading the class too early
    from renardo.renardo_app.renardo_app import RenardoApp
    # Reset the singleton instance
    RenardoApp._instance = None
    yield
    # Clean up after test
    RenardoApp._instance = None


@patch('renardo.renardo_app.renardo_app.argparse.ArgumentParser.parse_args')
@patch('renardo.renardo_app.renardo_app.SupercolliderInstance')
@patch('renardo.renardo_app.renardo_app.PulsarInstance')
def test_singleton_pattern(mock_pulsar, mock_sc, mock_parse_args):
    """Test that RenardoApp follows the singleton pattern"""
    # Set up mocks
    mock_parse_args.return_value = MagicMock()
    
    # Import here to avoid loading the class too early
    from renardo.renardo_app.renardo_app import RenardoApp
    from renardo.renardo_app import get_instance
    
    # Create an instance using the constructor
    app1 = RenardoApp.get_instance()
    
    # Try to create another instance using the constructor
    app2 = RenardoApp.get_instance()
    
    # Verify that both instances are the same object
    assert app1 is app2
    
    # Verify that get_instance returns the same instance
    app3 = get_instance()
    assert app1 is app3
    
    # Verify that trying to instantiate directly raises an error
    with pytest.raises(RuntimeError):
        RenardoApp()


@patch('renardo.renardo_app.renardo_app.argparse.ArgumentParser.parse_args')
@patch('renardo.renardo_app.renardo_app.SupercolliderInstance')
@patch('renardo.renardo_app.renardo_app.PulsarInstance')
def test_has_state_manager(mock_pulsar, mock_sc, mock_parse_args):
    """Test that RenardoApp creates a StateManager instance"""
    # Set up mocks
    mock_parse_args.return_value = MagicMock()
    
    # Import here to avoid loading the class too early
    from renardo.renardo_app.renardo_app import RenardoApp
    from renardo.renardo_app.state_manager import StateManager
    
    # Create an instance
    app = RenardoApp.get_instance()
    
    # Verify that app has a state_manager attribute
    assert hasattr(app, 'state_manager')
    
    # Import StateManager to check the type
    assert isinstance(app.state_manager, StateManager)


@patch('renardo.renardo_app.renardo_app.argparse.ArgumentParser.parse_args')
@patch('renardo.renardo_app.renardo_app.SupercolliderInstance')
@patch('renardo.renardo_app.renardo_app.PulsarInstance')
@patch('renardo.renardo_app.renardo_app.create_webapp')
def test_webapp_creation(mock_create_webapp, mock_pulsar, mock_sc, mock_parse_args):
    """Test that RenardoApp creates a webapp instance when requested"""
    # Set up mocks
    mock_parse_args.return_value = MagicMock()
    mock_webapp = MagicMock()
    mock_create_webapp.return_value = mock_webapp
    
    # Import here to avoid loading the class too early
    from renardo.renardo_app.renardo_app import RenardoApp
    
    # Create an instance
    app = RenardoApp.get_instance()
    
    # Verify that webapp is initially None
    assert app.webapp is None
    
    # Call create_webapp_instance
    result = app.create_webapp_instance()
    
    # Verify that create_webapp was called
    mock_create_webapp.assert_called_once()
    
    # Verify that webapp was set
    assert app.webapp is mock_webapp
    
    # Verify that the method returns the webapp
    assert result is mock_webapp
    
    # Call create_webapp_instance again
    mock_create_webapp.reset_mock()
    result = app.create_webapp_instance()
    
    # Verify that create_webapp was not called again
    mock_create_webapp.assert_not_called()
    
    # Verify that the method still returns the webapp
    assert result is mock_webapp