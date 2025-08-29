#!/usr/bin/env python3
"""Demo script for adding and renaming tracks via Rust OSC extension."""

import time
import sys
from pathlib import Path

# Add the renardo package to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from renardo.logger import get_logger
from renardo.reaper_backend.reaside import ReaperClient, Reaper

logger = get_logger("add_track_demo")

def main():
    print("=" * 60)
    print("Add Track & Rename Demo (Pure Rust OSC)")
    print("=" * 60)
    
    try:
        print("\nConnecting to REAPER...")
        client = ReaperClient()
        reaper = Reaper(client)
        project = reaper.current_project
        
        print(f"Current project: '{project.name}'")
        
        print("\n1. Adding a new track...")
        new_track = project.basic_add_track()
        
        if new_track:
            print(f"✓ Successfully added track at index: {new_track._index}")
            print(f"   Default track name: '{new_track.name}'")
            
            time.sleep(0.5)
            
            print("\n2. Renaming the new track...")
            new_name = f"Rust OSC Track {int(time.time())}"
            new_track.name = new_name
            
            time.sleep(0.5)
            
            print(f"   Set track name to: '{new_name}'")
            print(f"   Current track name: '{new_track.name}'")
            
            print("\n3. Testing track name getter...")
            retrieved_name = new_track.name
            print(f"   Retrieved track name: '{retrieved_name}'")
            
            if retrieved_name == new_name:
                print("   ✓ Track name getter/setter working correctly!")
            else:
                print("   ⚠ Track name mismatch - may indicate timing issues")
        else:
            print("✗ Failed to add track")
            print("   Ensure REAPER is running with Rust extension loaded")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Note: This requires REAPER to be running with the Rust extension loaded")
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("\nArchitecture:")
    print("- project.basic_add_track() → Rust OSC /project/add_track")
    print("- track.name getter → Rust OSC /track/name/get")  
    print("- track.name setter → Rust OSC /track/name/set")
    print("- Pure Rust OSC - no HTTP fallbacks")
    print("=" * 60)

if __name__ == "__main__":
    main()