#!/usr/bin/env python3
"""Demo script for pure Rust OSC project name handling (no HTTP fallback)."""

import sys
from pathlib import Path

# Add the renardo package to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from renardo.logger import get_logger
from renardo.reaper_backend.reaside import ReaperClient, Reaper

logger = get_logger("rust_osc_only_demo")

def main():
    print("=" * 60)
    print("Pure Rust OSC Project Name Demo")
    print("(No HTTP fallbacks - Rust OSC extension only)")
    print("=" * 60)
    
    try:
        print("\nTesting ReaProject name handling (Rust OSC only)...")
        
        client = ReaperClient()
        reaper = Reaper(client)
        project = reaper.current_project
        
        print(f"Current project name: '{project.name}'")
        
        print("Setting project name to 'Pure Rust OSC Test'...")
        project.name = "Pure Rust OSC Test"
        
        print(f"Project name after set: '{project.name}'")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Note: This requires REAPER to be running with the Rust extension loaded")
    
    print("\n" + "=" * 60)
    print("Architecture:")
    print("- ReaProject.name getter → Rust OSC only")  
    print("- ReaProject.name setter → Rust OSC only")
    print("- No HTTP fallbacks")
    print("- Progressive removal of old Lua server logic")
    print("=" * 60)

if __name__ == "__main__":
    main()