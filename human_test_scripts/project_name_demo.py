#!/usr/bin/env python3
"""Demo script for REAPER project name handling via Rust OSC extension."""

import time
import sys
from pathlib import Path

# Add the renardo package to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from renardo.logger import get_logger
from renardo.reaper_backend.reaside import ReaperClient, Reaper
from renardo.reaper_backend.reaside.tools.rust_osc_client import RustOscClient

logger = get_logger("project_name_demo")

def main():
    print("=" * 60)
    print("REAPER Project Name Demo")
    print("=" * 60)
    
    try:
        print("\n1. Testing direct Rust OSC communication...")
        
        # Test direct OSC communication
        with RustOscClient() as rust_client:
            print("   - Getting project name via Rust OSC...")
            name = rust_client.get_project_name()
            print(f"   - Current project name: '{name}'")
            
            if name:
                print(f"   - Attempting to set project name to 'Test Project'...")
                success = rust_client.set_project_name("Test Project")
                print(f"   - Set operation acknowledged: {success}")
                
                time.sleep(0.5)
                
                print("   - Getting project name again...")
                new_name = rust_client.get_project_name()
                print(f"   - Project name after set: '{new_name}'")
            else:
                print("   - Could not get project name (Rust extension may not be loaded)")
        
        print("\n2. Testing via ReaSide integration...")
        
        # Test via ReaSide (correct usage)
        try:
            client = ReaperClient()
            reaper = Reaper(client)
            project = reaper.current_project
            
            print("   - ReaSide is available")
            print(f"   - Current project via ReaSide: '{project.name}'")
            
            # Try setting name via ReaSide (will use Rust OSC if available)
            original_name = project.name
            test_name = f"Demo Project {int(time.time())}"
            
            print(f"   - Setting project name to: '{test_name}'")
            project.name = test_name
            
            time.sleep(0.5)
            
            print(f"   - Project name after set via ReaSide: '{project.name}'")
            
            # Restore original name
            if original_name and original_name != "Untitled":
                print(f"   - Restoring original name: '{original_name}'")
                project.name = original_name
                
        except Exception as e:
            print(f"   - ReaSide is not available: {e}")
            print("   - (REAPER may not be running)")
    
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("\nNotes:")
    print("- The Rust extension provides fast OSC-based communication")
    print("- Project name setting may be limited by REAPER's API")
    print("- ReaSide automatically falls back to HTTP if Rust OSC is unavailable")
    print("=" * 60)

if __name__ == "__main__":
    main()