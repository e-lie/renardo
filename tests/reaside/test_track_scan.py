#!/usr/bin/env python3
"""Test track scan functionality."""

import pytest
import time


def test_scan_track_complete_basic(test_track_with_fx, client):
    """Test basic track scan functionality with single FX."""
    # Add a couple more FX to make it interesting
    test_track_with_fx.add_fx("ReaComp")
    test_track_with_fx.add_fx("ReaVerb")
    
    # Perform track scan
    start_time = time.time()
    result = client.scan_track_complete(test_track_with_fx.index)
    scan_time = time.time() - start_time
    
    # Verify scan was successful
    assert result is not None, "Scan result should not be None"
    assert result.get("success") is True, f"Scan should succeed, got: {result}"
    assert "track" in result, "Result should contain track data"
    
    track_data = result["track"]
    
    # Verify basic track information
    assert track_data["index"] == test_track_with_fx.index, "Track index should match"
    assert track_data["name"] == test_track_with_fx.name, "Track name should match"
    assert track_data["fx_count"] == 3, "Should have 3 FX (ReaEQ, ReaComp, ReaVerb)"
    
    # Verify FX information
    assert "fx" in track_data, "Track data should contain FX list"
    assert len(track_data["fx"]) == 3, "Should have 3 FX in the list"
    
    # Verify each FX has required fields
    for i, fx in enumerate(track_data["fx"]):
        assert "index" in fx, f"FX {i} should have index"
        assert "name" in fx, f"FX {i} should have name"
        assert "enabled" in fx, f"FX {i} should have enabled state"
        assert "param_count" in fx, f"FX {i} should have param_count"
        assert "params" in fx, f"FX {i} should have params list"
        
        # Verify parameter structure
        if fx["param_count"] > 0:
            assert len(fx["params"]) == fx["param_count"], f"FX {i} param count mismatch"
            
            for j, param in enumerate(fx["params"]):
                assert "index" in param, f"FX {i} param {j} should have index"
                assert "name" in param, f"FX {i} param {j} should have name"
                assert "value" in param, f"FX {i} param {j} should have value"
                assert "min" in param, f"FX {i} param {j} should have min"
                assert "max" in param, f"FX {i} param {j} should have max"
                assert "formatted" in param, f"FX {i} param {j} should have formatted"
                
                # Verify parameter values are reasonable
                assert isinstance(param["value"], (int, float)), f"FX {i} param {j} value should be numeric"
                assert param["min"] <= param["value"] <= param["max"], f"FX {i} param {j} value should be within range"
    
    # Verify track properties
    assert "volume" in track_data, "Track should have volume"
    assert "pan" in track_data, "Track should have pan"
    assert "mute" in track_data, "Track should have mute state"
    assert "solo" in track_data, "Track should have solo state"
    assert "rec_arm" in track_data, "Track should have rec_arm state"
    
    # Verify sends information
    assert "send_count" in track_data, "Track should have send_count"
    assert "sends" in track_data, "Track should have sends list"
    
    # Performance check - should be fast
    assert scan_time < 1.0, f"Scan should complete in under 1 second, took {scan_time:.3f}s"
    
    # Calculate total parameters
    total_params = sum(fx["param_count"] for fx in track_data["fx"])
    assert total_params > 0, "Should have some parameters to scan"
    
    # Performance comparison
    estimated_individual_time = total_params * 0.4  # 400ms per param
    speedup = estimated_individual_time / scan_time if scan_time > 0 else 0
    
    print(f"Scan performance: {total_params} params in {scan_time:.3f}s ({speedup:.1f}x faster)")
    assert speedup > 10, f"Scan should be at least 10x faster, got {speedup:.1f}x"


def test_scan_track_complete_performance(clean_project, client):
    """Test track scan performance with complex FX setup."""
    # Create track with multiple FX including complex ones
    track = clean_project.add_track()
    track.name = "Performance Test Track"
    
    # Add various FX types (using only valid REAPER FX names)
    fx_list = ["ReaEQ", "ReaComp", "ReaVerb", "ReaDelay", "ReaGate"]
    
    for fx_name in fx_list:
        success = track.add_fx(fx_name)
        assert success, f"Failed to add {fx_name}"
    
    # Perform multiple scans to test consistency
    scan_times = []
    scan_results = []
    
    for i in range(3):
        start_time = time.time()
        result = client.scan_track_complete(track.index)
        scan_time = time.time() - start_time
        
        scan_times.append(scan_time)
        scan_results.append(result)
        
        # Each scan should succeed
        assert result is not None, f"Scan {i+1} result should not be None"
        assert result.get("success") is True, f"Scan {i+1} should succeed"
    
    # Verify consistency across scans
    first_result = scan_results[0]["track"]
    for i, result in enumerate(scan_results[1:], 1):
        track_data = result["track"]
        assert track_data["fx_count"] == first_result["fx_count"], f"FX count should be consistent across scans"
        assert len(track_data["fx"]) == len(first_result["fx"]), f"FX list length should be consistent"
        
        # Verify each FX has same parameter count
        for j, fx in enumerate(track_data["fx"]):
            assert fx["param_count"] == first_result["fx"][j]["param_count"], f"FX {j} param count should be consistent"
            assert fx["name"] == first_result["fx"][j]["name"], f"FX {j} name should be consistent"
    
    # Performance analysis
    avg_scan_time = sum(scan_times) / len(scan_times)
    min_scan_time = min(scan_times)
    max_scan_time = max(scan_times)
    
    total_params = sum(fx["param_count"] for fx in first_result["fx"])
    
    print(f"Performance analysis:")
    print(f"  FX count: {first_result['fx_count']}")
    print(f"  Total parameters: {total_params}")
    print(f"  Average scan time: {avg_scan_time:.3f}s")
    print(f"  Min scan time: {min_scan_time:.3f}s")
    print(f"  Max scan time: {max_scan_time:.3f}s")
    print(f"  Parameters per second: {total_params / avg_scan_time:.1f}")
    
    # Performance requirements
    assert avg_scan_time < 0.5, f"Average scan time should be under 0.5s, got {avg_scan_time:.3f}s"
    assert max_scan_time < 1.0, f"Max scan time should be under 1.0s, got {max_scan_time:.3f}s"
    
    # Consistency requirement
    time_variance = max_scan_time - min_scan_time
    assert time_variance < 0.3, f"Scan time variance should be under 0.3s, got {time_variance:.3f}s"
    
    # Performance comparison with individual calls
    estimated_individual_time = total_params * 0.4  # 400ms per param
    speedup = estimated_individual_time / avg_scan_time if avg_scan_time > 0 else 0
    
    print(f"  Estimated individual time: {estimated_individual_time:.1f}s")
    print(f"  Speedup: {speedup:.1f}x faster")
    
    assert speedup > 50, f"Scan should be at least 50x faster than individual calls, got {speedup:.1f}x"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])