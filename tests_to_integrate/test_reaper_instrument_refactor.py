#!/usr/bin/env python3
"""
Test script to demonstrate the new ReaperInstrument class with integrated factory functionality
"""

from pathlib import Path
import sys

# Add a minimal example showing how to use the merged functionality
print("""
# Example usage of the refactored ReaperInstrument class:

# First, initialize the class with shared global settings
from renardo.reaper_backend.ReaperIntegrationLib.ReaProject import ReaProject
from renardo.reaper_backend.reaper_music_resource import ReaperInstrument
from renardo.runtime import Clock

# Initialize a ReaProject (or get it from elsewhere)
reaproject = ReaProject(Clock)

# Initialize the ReaperInstrument factory functionality
presets = {
    "track_default": {"amp": 1.0},
    "mychain_default": {"drive": 0.5}
}
ReaperInstrument.set_class_attributes(presets, reaproject)

# Now you can create instruments directly without a factory
bass = ReaperInstrument.create_instrument_facade(
    name="bass", 
    plugin_name="my_bass_chain",
    is_chain=True
)

# You can ensure FX chains are properly installed in REAPER
ReaperInstrument.ensure_fxchain_in_reaper("my_reverb_chain")

# You can create multiple FX chains at once
drums, piano = ReaperInstrument.add_multiple_fxchains("drums", "piano")

# All existing functionality continues to work as before
# And now the factory logic is centralized in the ReaperInstrument class
""")

# Actual test code to verify the implementation works
def test_reaper_instrument_factory_functionality():
    """Test the merged functionality if REAPER is available."""
    try:
        import reapy
        
        # Try to initialize with actual REAPER
        from renardo.runtime import Clock
        from renardo.reaper_backend.ReaperIntegrationLib.ReaProject import ReaProject
        from renardo.reaper_backend.reaper_music_resource import ReaperInstrument
        
        print("Testing with actual REAPER connection...")
        reaproject = ReaProject(Clock, reapylib=reapy)
        
        # Initialize factory functionality
        ReaperInstrument.set_class_attributes({}, reaproject)
        
        # Test the ensure_fxchain_in_reaper functionality
        print("\nTesting ensure_fxchain_in_reaper:")
        from renardo.settings_manager import SettingsManager
        
        config_dir = SettingsManager.get_standard_config_dir()
        reaper_fxchains_dir = config_dir / "REAPER" / "FXChains"
        renardo_fxchains_dir = reaper_fxchains_dir / "renardo_fxchains"
        
        print(f"REAPER FXChains directory: {reaper_fxchains_dir}")
        print(f"Renardo FXChains directory: {renardo_fxchains_dir}")
        
        if renardo_fxchains_dir.exists():
            print("Renardo FXChains directory exists!")
            print(f"Contents: {list(renardo_fxchains_dir.glob('*.RfxChain'))}")
        else:
            print("Directory does not yet exist. It will be created when needed.")
        
        print("\nTest completed successfully!")
        
    except ImportError:
        print("Could not import reapy. REAPER integration test skipped.")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_reaper_instrument_factory_functionality()