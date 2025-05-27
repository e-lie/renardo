#!/usr/bin/env python3
"""
Test script for ensure_fxchain_in_reaper functionality
"""

from pathlib import Path
from renardo.settings_manager import settings, SettingsManager
from renardo.reaper_backend.ReaperIntegration import ReaperInstrumentFactory, init_reapy_project
from renardo.gatherer.reaper_resource_management.reaper_resource_library import ReaperResourceLibrary, ensure_reaper_directories

def test_ensure_fxchain():
    """Test the ensure_fxchain_in_reaper method."""
    print("Testing ensure_fxchain_in_reaper functionality...")
    
    # Create a mock ReaProject for testing
    reaproject = init_reapy_project()
    if not reaproject:
        print("No REAPER project detected. Creating mock factory for testing...")
        # Create a factory with None project for testing
        factory = ReaperInstrumentFactory({}, None)
    else:
        factory = ReaperInstrumentFactory({}, reaproject)
    
    # First, ensure we have a reaper_resources directory structure
    renardo_root = settings.get_path("RENARDO_ROOT_PATH")
    resources_path = ensure_reaper_directories(renardo_root)
    print(f"Resources path: {resources_path}")
    
    # Create a sample FXChain resource for testing
    test_bank_dir = resources_path / "0_test_bank"
    test_bank_dir.mkdir(exist_ok=True)
    
    instruments_dir = test_bank_dir / "instruments"
    instruments_dir.mkdir(exist_ok=True)
    
    test_category_dir = instruments_dir / "test_category"
    test_category_dir.mkdir(exist_ok=True)
    
    # Create a sample FXChain resource file
    test_resource_file = test_category_dir / "test_chain.py"
    test_resource_content = '''from renardo.reaper_backend.reaper_music_resource import ReaperInstrument

test_chain = ReaperInstrument(
    shortname="test_chain",
    fullname="Test FX Chain",
    description="A test FX chain for validation",
    fxchain_relative_path="test_chain.RfxChain",
    arguments={
        "amp": 1.0,
        "pan": 0.0
    },
    bank="test",
    category="test_category"
)
'''
    
    with open(test_resource_file, 'w') as f:
        f.write(test_resource_content)
    
    # Create a sample .RfxChain file
    test_fxchain_file = test_category_dir / "test_chain.RfxChain"
    test_fxchain_content = '''<FXCHAIN
SHOW 0
LASTSEL 0
DOCKED 0
BYPASS 0 0 0
<VST "VST: Test Plugin" test.vst 0 "" 1234567890<>
test_plugin_state
>
FLOATPOS 0 0 0 0
FXID {12345678-1234-1234-1234-123456789012}
WAK 0
>
'''
    
    with open(test_fxchain_file, 'w') as f:
        f.write(test_fxchain_content)
    
    # Now test the ensure_fxchain_in_reaper method
    print("\n1. Testing with existing FXChain resource...")
    success = factory.ensure_fxchain_in_reaper("test_chain")
    print(f"Result: {'Success' if success else 'Failed'}")
    
    # Check if the file was copied
    config_dir = SettingsManager.get_standard_config_dir()
    expected_path = config_dir / "REAPER" / "FXChains" / "renardo_fxchains" / "test_chain.RfxChain"
    print(f"Expected path: {expected_path}")
    print(f"File exists: {expected_path.exists()}")
    
    # Test with non-existent resource
    print("\n2. Testing with non-existent FXChain resource...")
    success = factory.ensure_fxchain_in_reaper("non_existent_chain")
    print(f"Result: {'Success' if success else 'Failed'} (expected to fail)")
    
    # Test updating existing FXChain
    print("\n3. Testing updating existing FXChain...")
    success = factory.ensure_fxchain_in_reaper("test_chain")
    print(f"Result: {'Success' if success else 'Failed'} (should report already up to date)")
    
    # Clean up - optionally remove test files
    # test_resource_file.unlink()
    # test_fxchain_file.unlink()
    # test_category_dir.rmdir()
    # instruments_dir.rmdir() 
    # test_bank_dir.rmdir()
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_ensure_fxchain()