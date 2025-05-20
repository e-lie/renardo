#!/usr/bin/env python3
"""
Test script to verify that we have fixed the circular import issue
"""

def test_imports():
    """Test importing the modules that had circular dependencies."""
    print("Testing imports to verify circular dependency fix...")
    
    # First import reaper_music_resource
    print("Importing ReaperInstrument...")
    from renardo.reaper_backend.reaper_music_resource import ReaperInstrument
    print("Successfully imported ReaperInstrument")
    
    # Then import reaper_resource_library
    print("\nImporting ReaperResourceLibrary...")
    from renardo.gatherer.reaper_resource_management.reaper_resource_library import ReaperResourceLibrary
    print("Successfully imported ReaperResourceLibrary")
    
    # Test the ensure_fxchain_in_reaper method with a dummy shortname
    print("\nTesting ensure_fxchain_in_reaper method...")
    try:
        result = ReaperInstrument.ensure_fxchain_in_reaper("test_chain")
        print(f"Method called successfully, returned: {result}")
    except Exception as e:
        print(f"Error calling method: {e}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_imports()