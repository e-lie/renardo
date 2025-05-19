#!/usr/bin/env python3
"""
Migration script to move tutorial files from demo/demo_esp to tutorial/en/es structure
"""

import os
import shutil
from pathlib import Path

def migrate_tutorials(base_path):
    """Migrate tutorial files to new structure"""
    
    # Define old and new paths
    demo_path = base_path / "demo"
    demo_esp_path = base_path / "demo_esp"
    tutorial_path = base_path / "tutorial"
    
    # Create new structure
    en_path = tutorial_path / "en"
    es_path = tutorial_path / "es"
    
    # Check if migration is needed
    if not demo_path.exists() and not demo_esp_path.exists():
        print("No migration needed - demo directories not found")
        return False
        
    print("Starting tutorial migration...")
    
    # Create tutorial directories
    tutorial_path.mkdir(exist_ok=True)
    en_path.mkdir(exist_ok=True)
    es_path.mkdir(exist_ok=True)
    
    # Move English tutorials
    if demo_path.exists():
        for file in demo_path.glob("*.py"):
            dest = en_path / file.name
            print(f"Moving {file} to {dest}")
            shutil.move(str(file), str(dest))
        # Remove empty directory
        try:
            demo_path.rmdir()
            print(f"Removed empty directory: {demo_path}")
        except OSError:
            print(f"Directory not empty: {demo_path}")
    
    # Move Spanish tutorials
    if demo_esp_path.exists():
        for file in demo_esp_path.glob("*.py"):
            dest = es_path / file.name
            print(f"Moving {file} to {dest}")
            shutil.move(str(file), str(dest))
        # Remove empty directory
        try:
            demo_esp_path.rmdir()
            print(f"Removed empty directory: {demo_esp_path}")
        except OSError:
            print(f"Directory not empty: {demo_esp_path}")
    
    print("Tutorial migration completed successfully!")
    return True

if __name__ == "__main__":
    # Get the renardo source directory
    script_dir = Path(__file__).parent
    renardo_dir = script_dir.parent / "src" / "renardo"
    
    if renardo_dir.exists():
        migrate_tutorials(renardo_dir)
    else:
        print(f"Error: Renardo directory not found at {renardo_dir}")