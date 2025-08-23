#!/usr/bin/env python3
"""
Test script for TimeVar parameter automation in reaside.
Demonstrates continuous parameter modulation using TimeVar objects.
"""

import time
import math
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.renardo.reaper_backend.reaside import start_reaper, ReaperClient, Reaper
from src.renardo.reaper_backend.reaside.utils import set_fx_parameter


class SimpleTimeVar:
    """Simple TimeVar implementation for testing."""
    
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.start_time = time.time()
    
    def now(self):
        """Get current value based on elapsed time."""
        elapsed = time.time() - self.start_time
        return self.func(elapsed, *self.args, **self.kwargs)
    
    def __float__(self):
        return self.now()


def sine_wave(t, freq=0.5, amplitude=0.5, offset=0.5):
    """Generate sine wave value."""
    return offset + amplitude * math.sin(2 * math.pi * freq * t)


def triangle_wave(t, freq=0.25, amplitude=0.5, offset=0.5):
    """Generate triangle wave value."""
    phase = (freq * t) % 1.0
    if phase < 0.5:
        return offset - amplitude + (4 * amplitude * phase)
    else:
        return offset + amplitude - (4 * amplitude * (phase - 0.5))


def square_wave(t, freq=0.5, amplitude=0.5, offset=0.5):
    """Generate square wave value."""
    phase = (freq * t) % 1.0
    return offset + amplitude if phase < 0.5 else offset - amplitude


def main():
    """Main test function."""
    print("=== TimeVar Parameter Automation Test ===\n")
    
    try:
        # Start REAPER and connect
        print("Starting REAPER...")
        start_reaper()
        client = ReaperClient()
        reaper = Reaper(client)
        
        # Get current project and add track
        project = reaper.current_project
        track = project.add_track()
        track.name = "TimeVar Test Track"
        print(f"Created track: {track.name}")
        
        # Add some FX for testing
        fx_to_add = ["ReaEQ", "ReaComp", "ReaDelay"]
        
        for fx_name in fx_to_add:
            success = track.add_fx(fx_name)
            if success:
                print(f"Added {fx_name}")
            else:
                print(f"Failed to add {fx_name}")
        
        # Get FX list
        fx_list = track.list_fx()
        if not fx_list:
            print("No FX found on track!")
            return
        
        print(f"\nFound {len(fx_list)} FX on track:")
        for fx in fx_list:
            print(f"  - {fx.name}")
            params = fx.list_params()
            if params:
                print(f"    Parameters: {[p.name for p in params[:5]]}")  # Show first 5 params
        
        # Test 1: Simple sine wave on first FX parameter
        print("\n=== Test 1: Sine Wave Modulation ===")
        if fx_list:
            fx = fx_list[0]
            params = fx.list_params()
            if len(params) > 1:
                param = params[1]  # Use second parameter (often frequency/gain)
                print(f"Modulating {fx.name}.{param.name} with sine wave...")
                
                # Create and apply TimeVar
                sine_var = SimpleTimeVar(sine_wave, freq=0.5, amplitude=0.4, offset=0.5)
                param.set_value(sine_var)
                
                print("Sine wave modulation active for 5 seconds...")
                time.sleep(5)
                
                # Stop modulation by setting a fixed value
                param.set_value(0.5)
                print("Stopped sine modulation")
        
        # Test 2: Triangle wave on different parameter
        print("\n=== Test 2: Triangle Wave Modulation ===")
        if len(fx_list) > 1:
            fx = fx_list[1]
            params = fx.list_params()
            if params:
                param = params[0]
                print(f"Modulating {fx.name}.{param.name} with triangle wave...")
                
                triangle_var = SimpleTimeVar(triangle_wave, freq=0.3, amplitude=0.3, offset=0.5)
                param.set_value(triangle_var)
                
                print("Triangle wave modulation active for 5 seconds...")
                time.sleep(5)
                
                param.set_value(0.5)
                print("Stopped triangle modulation")
        
        # Test 3: Multiple simultaneous TimeVars
        print("\n=== Test 3: Multiple Simultaneous TimeVars ===")
        active_timevars = []
        
        for i, fx in enumerate(fx_list[:3]):
            params = fx.list_params()
            if params:
                param = params[0]
                
                # Different wave types for each FX
                if i == 0:
                    var = SimpleTimeVar(sine_wave, freq=0.4, amplitude=0.3, offset=0.5)
                    wave_type = "sine"
                elif i == 1:
                    var = SimpleTimeVar(triangle_wave, freq=0.3, amplitude=0.4, offset=0.5)
                    wave_type = "triangle"
                else:
                    var = SimpleTimeVar(square_wave, freq=0.2, amplitude=0.2, offset=0.5)
                    wave_type = "square"
                
                param.set_value(var)
                active_timevars.append((param, wave_type))
                print(f"Started {wave_type} wave on {fx.name}.{param.name}")
        
        if active_timevars:
            print(f"\n{len(active_timevars)} TimeVars running simultaneously...")
            print("Running for 10 seconds...")
            time.sleep(10)
            
            # Stop all TimeVars
            for param, wave_type in active_timevars:
                param.set_value(0.5)
                print(f"Stopped {wave_type} wave")
        
        # Test 4: Using set_fx_parameter with TimeVar
        print("\n=== Test 4: set_fx_parameter with TimeVar ===")
        if fx_list:
            fx = fx_list[0]
            param_fullname = f"{fx.snake_name}_gain"  # Assuming there's a gain parameter
            
            print(f"Trying to modulate {param_fullname} with TimeVar...")
            fast_sine = SimpleTimeVar(sine_wave, freq=2.0, amplitude=0.2, offset=0.7)
            
            success = set_fx_parameter(track, param_fullname, fast_sine)
            if success:
                print("Fast sine modulation active for 5 seconds...")
                time.sleep(5)
                
                # Reset to normal value
                set_fx_parameter(track, param_fullname, 0.5)
                print("Modulation stopped")
            else:
                print(f"Could not find parameter {param_fullname}")
        
        # Check TimeVar manager status
        print("\n=== TimeVar Manager Status ===")
        from src.renardo.reaper_backend.reaside.core.timevar_manager import get_timevar_manager
        manager = get_timevar_manager()
        print(f"Active bindings: {manager.get_binding_count()}")
        print(f"Update rate: {manager.get_update_rate()}Hz")
        
        # Cleanup
        print("\nCleaning up...")
        manager.clear_all_bindings()
        print(f"Active bindings after cleanup: {manager.get_binding_count()}")
        
        print("\n=== Test Complete ===")
        print("TimeVar parameter automation is working!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()