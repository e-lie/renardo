#!/usr/bin/env python3
"""
Test script for user directory functionality
"""

from renardo.settings_manager import settings, SettingsManager
from pathlib import Path
import tempfile
import shutil

def test_user_directory_functionality():
    print("Testing user directory functionality...")
    
    # 1. Test getting current user directory
    current_dir = settings.get_renardo_user_dir()
    print(f"Current user directory: {current_dir}")
    
    # 2. Test that the get_standard_user_dir works
    standard_dir = SettingsManager.get_standard_user_dir()
    print(f"Standard user directory: {standard_dir}")
    
    # 3. Test setting a new user directory path
    with tempfile.TemporaryDirectory() as temp_dir:
        new_path = Path(temp_dir) / "test_renardo_user"
        new_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\nTesting set_user_dir_path with: {new_path}")
        success = SettingsManager.set_user_dir_path(new_path)
        print(f"Set user dir path success: {success}")
        
        # Check that user_dir.toml was created
        user_dir_toml = standard_dir / "user_dir.toml"
        print(f"user_dir.toml exists: {user_dir_toml.exists()}")
        
        if user_dir_toml.exists():
            with open(user_dir_toml, 'r') as f:
                content = f.read()
                print(f"user_dir.toml content:\n{content}")
    
    # 4. Test that get_path methods work correctly
    print("\nTesting get_path methods:")
    print(f"PUBLIC_SETTINGS_FILE: {settings.get_path('PUBLIC_SETTINGS_FILE')}")
    print(f"INTERNAL_SETTINGS_FILE: {settings.get_path('INTERNAL_SETTINGS_FILE')}")
    print(f"SAMPLES_DIR: {settings.get_path('SAMPLES_DIR')}")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    test_user_directory_functionality()