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
    on_param = reafx_instance.get_param('on')
    assert on_param is not None, "Should have 'on' parameter"
    on_value = on_param.get_value()
    assert isinstance(on_value, (int, float)), "On parameter should be numeric"


def test_reafx_set_on_parameter(reafx_instance):
    """Test setting the 'on' parameter."""
    on_param = reafx_instance.get_param('on')
    assert on_param is not None, "Should have 'on' parameter"
    
    # Set to on
    on_param.set_value(1.0)
    on_value = on_param.get_value()
    assert abs(on_value - 1.0) < 0.1, "On parameter should be set to 1.0"
    
    # Set to off
    on_param.set_value(0.0)
    on_value = on_param.get_value()
    assert abs(on_value - 0.0) < 0.1, "On parameter should be set to 0.0"


def test_reafx_enable_disable(reafx_instance):
    """Test enabling and disabling FX."""
    # Enable FX
    reafx_instance.enable()
    assert reafx_instance.is_enabled(), "FX should be enabled"
    
    # Disable FX
    reafx_instance.disable()
    assert not reafx_instance.is_enabled(), "FX should be disabled"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])