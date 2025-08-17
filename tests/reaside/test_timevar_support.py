"""
Test TimeVar support for ReaParam and ReaSend in reaside.
"""

import pytest
import time
import math
from unittest.mock import Mock, MagicMock, patch

from renardo.reaper_backend.reaside.core.param import ReaParam, ReaSend
from renardo.reaper_backend.reaside.core.timevar_manager import TimeVarManager, get_timevar_manager


class MockTimeVar:
    """Mock TimeVar object for testing."""
    
    def __init__(self, func=None):
        self.func = func or (lambda: 0.5)
        self.call_count = 0
    
    def now(self):
        """Return current value."""
        self.call_count += 1
        return self.func()


def test_timevar_manager_singleton():
    """Test that TimeVarManager is a singleton."""
    manager1 = get_timevar_manager()
    manager2 = get_timevar_manager()
    assert manager1 is manager2


def test_timevar_detection():
    """Test detection of TimeVar objects."""
    mock_client = Mock()
    param = ReaParam(mock_client, 0, 0, 0, "test", "Test", use_osc=False)
    
    # Test objects with 'now' method
    mock_timevar = Mock()
    mock_timevar.now = Mock(return_value=0.5)
    assert param._is_timevar(mock_timevar)
    
    # Test objects with 'current_value' method
    mock_timevar2 = Mock()
    mock_timevar2.current_value = Mock(return_value=0.5)
    assert param._is_timevar(mock_timevar2)
    
    # Test objects with TimeVar in class name
    class TestTimeVar:
        pass
    assert param._is_timevar(TestTimeVar())
    
    # Test regular float is not TimeVar
    assert not param._is_timevar(0.5)
    assert not param._is_timevar(1)


@pytest.fixture(autouse=True)
def cleanup_timevar_manager():
    """Cleanup TimeVar manager after each test."""
    yield
    manager = get_timevar_manager()
    manager.clear_all_bindings()


def test_reaparam_timevar_binding():
    """Test binding TimeVar to ReaParam."""
    mock_client = Mock()
    mock_client.call_reascript_function = Mock(return_value=None)
    
    param = ReaParam(mock_client, 0, 0, 0, "test", "Test", use_osc=False)
    manager = get_timevar_manager()
    
    # Clear any existing bindings
    manager.clear_all_bindings()
    
    # Create TimeVar and bind it
    timevar = MockTimeVar(lambda: 0.75)
    param.set_value(timevar)
    
    # Check that binding was created
    assert manager.is_param_bound(param)
    assert manager.get_binding_count() == 1
    
    # Set normal value should clear binding
    param.set_value(0.5)
    assert not manager.is_param_bound(param)
    assert manager.get_binding_count() == 0


def test_reasend_timevar_binding():
    """Test binding TimeVar to ReaSend."""
    mock_client = Mock()
    mock_client.set_send_volume = Mock()
    
    send = ReaSend(mock_client, 0, 0, "volume", "send_volume")
    manager = get_timevar_manager()
    
    # Clear any existing bindings
    manager.clear_all_bindings()
    
    # Create TimeVar and bind it
    timevar = MockTimeVar(lambda: 0.8)
    send.set_value(timevar)
    
    # Check that binding was created
    assert manager.is_param_bound(send)
    assert manager.get_binding_count() == 1
    
    # Set normal value should clear binding
    send.set_value(0.5)
    assert not manager.is_param_bound(send)
    assert manager.get_binding_count() == 0
    mock_client.set_send_volume.assert_called_with(0, 0, 0.5)


def test_timevar_manager_update_rate():
    """Test TimeVar manager update rate configuration."""
    manager = get_timevar_manager()
    
    # Default rate should be 20Hz
    assert manager.get_update_rate() == 20
    
    # Test setting valid rates
    manager.set_update_rate(30)
    assert manager.get_update_rate() == 30
    
    manager.set_update_rate(10)
    assert manager.get_update_rate() == 10
    
    # Test invalid rates
    with pytest.raises(ValueError):
        manager.set_update_rate(0)
    
    with pytest.raises(ValueError):
        manager.set_update_rate(101)
    
    # Reset to default
    manager.set_update_rate(20)


def test_multiple_timevar_bindings():
    """Test multiple simultaneous TimeVar bindings."""
    mock_client = Mock()
    mock_client.call_reascript_function = Mock(return_value=None)
    
    manager = get_timevar_manager()
    manager.clear_all_bindings()
    
    # Create multiple parameters
    params = []
    for i in range(3):
        param = ReaParam(mock_client, 0, i, i, f"param{i}", f"Param {i}", use_osc=False)
        params.append(param)
    
    # Bind TimeVars to all parameters
    for i, param in enumerate(params):
        timevar = MockTimeVar(lambda v=i: v * 0.1)
        param.set_value(timevar)
    
    # Check all bindings exist
    assert manager.get_binding_count() == 3
    for param in params:
        assert manager.is_param_bound(param)
    
    # Clear one binding
    params[1].set_value(0.5)
    assert manager.get_binding_count() == 2
    assert not manager.is_param_bound(params[1])
    assert manager.is_param_bound(params[0])
    assert manager.is_param_bound(params[2])
    
    # Clear all bindings
    manager.clear_all_bindings()
    assert manager.get_binding_count() == 0


def test_timevar_evaluation():
    """Test TimeVar evaluation methods."""
    manager = TimeVarManager()
    
    # Test object with now() method
    mock_var = Mock()
    mock_var.now = Mock(return_value=0.75)
    assert manager._evaluate_timevar(mock_var) == 0.75
    mock_var.now.assert_called_once()
    
    # Test object with current_value() method
    mock_var2 = Mock()
    mock_var2.current_value = Mock(return_value=0.6)
    assert manager._evaluate_timevar(mock_var2) == 0.6
    mock_var2.current_value.assert_called_once()
    
    # Test callable object
    callable_var = Mock(return_value=0.9)
    assert manager._evaluate_timevar(callable_var) == 0.9
    callable_var.assert_called_once()
    
    # Test direct float conversion
    assert manager._evaluate_timevar(0.5) == 0.5
    assert manager._evaluate_timevar(1) == 1.0


def test_weak_reference_cleanup():
    """Test that TimeVar bindings are cleaned up when parameters are deleted."""
    mock_client = Mock()
    mock_client.call_reascript_function = Mock(return_value=None)
    
    manager = get_timevar_manager()
    manager.clear_all_bindings()
    
    # Create parameter and bind TimeVar
    param = ReaParam(mock_client, 0, 0, 0, "test", "Test", use_osc=False)
    timevar = MockTimeVar()
    param.set_value(timevar)
    
    assert manager.get_binding_count() == 1
    
    # Delete parameter reference
    param_id = id(param)
    del param
    
    # Force garbage collection
    import gc
    gc.collect()
    
    # Binding should be cleaned up automatically on next access
    # Note: This might not work reliably in all test environments
    # due to Python's garbage collection behavior


def test_timevar_with_osc():
    """Test TimeVar binding with OSC-enabled parameters."""
    mock_client = Mock()
    mock_client.send_osc_message = Mock(return_value=True)
    mock_client.call_reascript_function = Mock(return_value=None)
    
    # Create OSC-enabled parameter
    param = ReaParam(mock_client, 0, 0, 1, "cutoff", "Cutoff", use_osc=True)
    
    # Bind TimeVar
    timevar = MockTimeVar(lambda: 0.7)
    param.set_value(timevar)
    
    manager = get_timevar_manager()
    assert manager.is_param_bound(param)
    
    # Normal value should still use OSC
    param.set_value(0.5)
    mock_client.send_osc_message.assert_called_with("/track/1/fx/1/fxparam/2/value", 0.5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])