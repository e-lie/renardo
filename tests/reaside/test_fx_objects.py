#!/usr/bin/env python3
"""Test FX object functionality."""

import pytest
from renardo.reaper_backend.reaside.core.fx import ReaFX


def test_reafx_creation(client, test_track_with_fx):
    """Test creating ReaFX object."""
    fx = ReaFX(client, test_track_with_fx.index, 0, "ReaEQ")
    assert fx is not None, "ReaFX object should be created"
    assert fx.track_index == test_track_with_fx.index, "Track index should match"
    assert fx.fx_index == 0, "FX index should be 0"
    assert fx.name == "ReaEQ", "FX name should match"


def test_reafx_param_names(reafx_instance):
    """Test getting parameter names from ReaFX."""
    param_names = reafx_instance.get_param_names()
    assert isinstance(param_names, list), "Parameter names should be a list"
    assert len(param_names) > 0, "Should have at least one parameter"
    assert 'on' in param_names, "Should have 'on' parameter"


def test_reafx_on_parameter(reafx_instance):
    """Test the 'on' parameter which should always exist."""
    on_value = reafx_instance.get_param('on')
    assert isinstance(on_value, (int, float)), "On parameter should be numeric"
    assert 0.0 <= on_value <= 1.0, "On parameter should be between 0 and 1"


def test_reafx_set_on_parameter(reafx_instance):
    """Test setting the 'on' parameter."""
    # Set to on
    reafx_instance.set_param('on', 1.0)
    on_value = reafx_instance.get_param('on')
    assert on_value == 1.0, "On parameter should be set to 1.0"
    
    # Set to off
    reafx_instance.set_param('on', 0.0)
    on_value = reafx_instance.get_param('on')
    assert on_value == 0.0, "On parameter should be set to 0.0"


def test_reafx_enable_disable(reafx_instance):
    """Test enabling and disabling FX."""
    # Enable FX
    reafx_instance.enable()
    assert reafx_instance.is_enabled(), "FX should be enabled"
    
    # Disable FX
    reafx_instance.disable()
    assert not reafx_instance.is_enabled(), "FX should be disabled"


def test_reafx_is_enabled_initial(reafx_instance):
    """Test initial enabled state."""
    is_enabled = reafx_instance.is_enabled()
    assert isinstance(is_enabled, bool), "Enabled state should be boolean"


def test_reafx_get_nonexistent_param(reafx_instance):
    """Test getting non-existent parameter."""
    value = reafx_instance.get_param('nonexistent_param')
    assert value is None, "Non-existent parameter should return None"


def test_reafx_set_nonexistent_param(reafx_instance):
    """Test setting non-existent parameter."""
    # Should not raise an error, just silently fail
    reafx_instance.set_param('nonexistent_param', 0.5)
    value = reafx_instance.get_param('nonexistent_param')
    assert value is None, "Non-existent parameter should still return None"


def test_reafx_update_params(reafx_instance):
    """Test updating all parameters."""
    # This should not raise an error
    reafx_instance.update_params()
    
    # Parameters should still be accessible
    param_names = reafx_instance.get_param_names()
    assert len(param_names) > 0, "Should still have parameters after update"


def test_reafx_get_all_params(reafx_instance):
    """Test getting all parameters with prefixes."""
    all_params = reafx_instance.get_all_params()
    assert isinstance(all_params, dict), "All params should be a dictionary"
    assert len(all_params) > 0, "Should have at least one parameter"
    
    # Check that parameters are prefixed with FX name
    for param_name in all_params.keys():
        assert param_name.startswith("ReaEQ_"), f"Parameter {param_name} should start with 'ReaEQ_'"


def test_reafx_param_values_numeric(reafx_instance):
    """Test that all parameter values are numeric."""
    param_names = reafx_instance.get_param_names()
    
    for param_name in param_names:
        value = reafx_instance.get_param(param_name)
        assert isinstance(value, (int, float)), f"Parameter {param_name} value should be numeric, got {type(value)}"


def test_reafx_param_values_range(reafx_instance):
    """Test that parameter values are in expected range."""
    param_names = reafx_instance.get_param_names()
    
    for param_name in param_names:
        value = reafx_instance.get_param(param_name)
        # Most REAPER parameters are normalized 0-1
        assert 0.0 <= value <= 1.0, f"Parameter {param_name} value {value} should be between 0 and 1"


def test_reafx_multiple_instances(client, test_track):
    """Test creating multiple ReaFX instances."""
    # Add multiple FX
    test_track.add_fx("ReaEQ")
    test_track.add_fx("ReaComp")
    
    # Create FX objects
    fx1 = ReaFX(client, test_track.index, 0, "ReaEQ")
    fx2 = ReaFX(client, test_track.index, 1, "ReaComp")
    
    # Both should be independent
    assert fx1.fx_index != fx2.fx_index, "FX instances should have different indices"
    assert fx1.name != fx2.name, "FX instances should have different names"
    
    # Both should have parameters
    params1 = fx1.get_param_names()
    params2 = fx2.get_param_names()
    assert len(params1) > 0, "First FX should have parameters"
    assert len(params2) > 0, "Second FX should have parameters"


def test_reafx_param_persistence(reafx_instance):
    """Test that parameter changes persist."""
    # Set a parameter
    reafx_instance.set_param('on', 0.5)
    
    # Get the value back
    value = reafx_instance.get_param('on')
    assert value == 0.5, "Parameter value should persist"
    
    # Update all parameters and check again
    reafx_instance.update_params()
    value = reafx_instance.get_param('on')
    assert value == 0.5, "Parameter value should persist after update"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])