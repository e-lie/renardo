#!/usr/bin/env python3
"""Test new FX API with automatic scanning and OSC integration."""

import pytest
import time


def test_track_automatic_scanning(test_track, client):
    """Test that track automatically scans FX on creation."""
    # Track should have been automatically scanned
    assert hasattr(test_track, '_scan_data'), "Track should have scan data"
    assert hasattr(test_track, '_fx_objects'), "Track should have FX objects cache"
    
    # Initially should have no FX
    fx_list = test_track.list_fx()
    assert len(fx_list) == 0, "New track should have no FX"


def test_fx_object_creation_on_add(test_track, client):
    """Test that FX objects are created when FX is added."""
    # Add FX - this should trigger rescan and create objects
    success = test_track.add_fx("ReaEQ")
    assert success, "Should be able to add ReaEQ"
    
    # Check that FX objects were created
    fx_list = test_track.list_fx()
    assert len(fx_list) == 1, "Should have one FX after adding ReaEQ"
    
    # Check FX object properties
    reaeq = fx_list[0]
    assert reaeq.name == "VST: ReaEQ (Cockos)", "FX should have correct name"
    assert reaeq.reaper_name == "VST: ReaEQ (Cockos)", "FX should have reaper_name"
    assert reaeq.snake_name == "rea_eq", "FX should have snake_name"
    assert reaeq.track_index == test_track.index, "FX should have correct track index"
    assert reaeq.fx_index == 0, "First FX should have index 0"


def test_fx_access_by_name(test_track, client):
    """Test accessing FX by various name formats."""
    # Add FX
    test_track.add_fx("ReaEQ")
    
    # Access by snake_case name
    reaeq1 = test_track.get_fx_by_name("rea_eq")
    assert reaeq1 is not None, "Should find FX by snake_case name"
    
    # Access by original name
    reaeq2 = test_track.get_fx_by_name("VST: ReaEQ (Cockos)")
    assert reaeq2 is not None, "Should find FX by original name"
    
    # Should be the same object
    assert reaeq1 is reaeq2, "Should return same object for different name formats"
    
    # Access by index
    reaeq3 = test_track.get_fx(0)
    assert reaeq3 is not None, "Should find FX by index"
    assert reaeq3 is reaeq1, "Should return same object for index access"


def test_fx_access_by_attribute(test_track, client):
    """Test accessing FX as track attributes."""
    # Add FX
    test_track.add_fx("ReaEQ")
    
    # Access as attribute
    reaeq = test_track.rea_eq
    assert reaeq is not None, "Should access FX as attribute"
    assert reaeq.name == "VST: ReaEQ (Cockos)", "Attribute access should return correct FX"
    
    # Test that non-existent FX raises AttributeError
    with pytest.raises(AttributeError):
        _ = test_track.nonexistent_fx


def test_fx_parameters_creation(test_track, client):
    """Test that FX parameters are created correctly."""
    # Add FX
    test_track.add_fx("ReaEQ")
    reaeq = test_track.get_fx(0)
    
    # Should have parameters
    assert len(reaeq.params) > 0, "FX should have parameters"
    
    # Should have 'on' parameter
    assert 'on' in reaeq.params, "FX should have 'on' parameter"
    on_param = reaeq.params['on']
    assert on_param.name == 'on', "Parameter should have snake_case name"
    assert on_param.reaper_name == 'FX Enabled', "Parameter should have reaper_name"
    assert on_param.param_index == -1, "On parameter should have special index"
    
    # Test parameter access methods
    on_param2 = reaeq.get_param('on')
    assert on_param2 is on_param, "get_param should return same object"
    
    # Test parameter list
    param_list = reaeq.list_params()
    assert len(param_list) == len(reaeq.params), "list_params should return all parameters"
    assert on_param in param_list, "on parameter should be in list"


def test_parameter_access_by_attribute(test_track, client):
    """Test accessing parameters as FX attributes."""
    # Add FX
    test_track.add_fx("ReaEQ")
    reaeq = test_track.get_fx(0)
    
    # Access parameter as attribute
    on_param = reaeq.on
    assert on_param is not None, "Should access parameter as attribute"
    assert on_param.name == 'on', "Attribute access should return correct parameter"
    
    # Test that non-existent parameter raises AttributeError
    with pytest.raises(AttributeError):
        _ = reaeq.nonexistent_param


def test_parameter_values_and_osc(test_track, client):
    """Test parameter value getting and setting."""
    # Add FX
    test_track.add_fx("ReaEQ")
    reaeq = test_track.get_fx(0)
    on_param = reaeq.on
    
    # Test getting value
    value = on_param.get_value()
    assert isinstance(value, float), "Parameter value should be float"
    assert 0.0 <= value <= 1.0, "Parameter value should be in valid range"
    
    # Test setting value
    original_value = on_param.get_value()
    new_value = 0.0 if original_value > 0.5 else 1.0
    on_param.set_value(new_value)
    
    # Value should be updated (may not be exact due to REAPER processing)
    updated_value = on_param.get_value()
    assert abs(updated_value - new_value) < 0.1, "Parameter value should be updated"
    
    # Test float conversion
    float_value = float(on_param)
    assert float_value == updated_value, "Parameter should convert to float"


def test_multiple_fx_management(test_track, client):
    """Test managing multiple FX on a track."""
    # Add multiple FX
    test_track.add_fx("ReaEQ")
    test_track.add_fx("ReaComp")
    test_track.add_fx("ReaVerb")
    
    # Check all FX are present
    fx_list = test_track.list_fx()
    assert len(fx_list) == 3, "Should have three FX"
    
    # Check FX indices
    for i, fx in enumerate(fx_list):
        assert fx.fx_index == i, f"FX {i} should have correct index"
    
    # Check access by snake_case names
    reaeq = test_track.rea_eq
    reacomp = test_track.rea_comp
    reaverb = test_track.rea_verb
    
    assert reaeq is not None, "Should access ReaEQ"
    assert reacomp is not None, "Should access ReaComp"
    assert reaverb is not None, "Should access ReaVerb"
    
    # Check they're different objects
    assert reaeq is not reacomp, "Different FX should be different objects"
    assert reacomp is not reaverb, "Different FX should be different objects"


def test_rescan_functionality(test_track, client):
    """Test manual rescan functionality."""
    # Add FX
    test_track.add_fx("ReaEQ")
    original_fx_count = len(test_track.list_fx())
    
    # Manual rescan should work
    test_track.rescan_fx()
    
    # Should still have the same FX
    new_fx_count = len(test_track.list_fx())
    assert new_fx_count == original_fx_count, "Rescan should maintain FX count"
    
    # FX should still be accessible
    reaeq = test_track.get_fx(0)
    assert reaeq is not None, "FX should still be accessible after rescan"


def test_snake_case_conversion(test_track, client):
    """Test snake_case name conversion."""
    # Add FX with complex name
    test_track.add_fx("ReaEQ")
    reaeq = test_track.get_fx(0)
    
    # Check snake_case conversion
    assert reaeq.snake_name == "rea_eq", "Complex name should convert to snake_case"
    
    # Test parameter snake_case conversion
    params = reaeq.list_params()
    for param in params:
        # All parameter names should be valid Python identifiers
        assert param.name.isidentifier(), f"Parameter name '{param.name}' should be valid identifier"
        assert param.name.islower(), f"Parameter name '{param.name}' should be lowercase"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])