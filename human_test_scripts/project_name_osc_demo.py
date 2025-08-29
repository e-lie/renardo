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

logger = get_logger("project_name_osc_demo")

def main():
    print("=" * 60)
    print("REAPER Project Name OSC Demo")
    print("=" * 60)
    
    try:
        print("\n1. Testing direct Rust OSC communication...")
        
        # Test direct OSC communication
        with RustOscClient() as rust_client:
            print("   - Getting project name via Rust OSC...")
            name = rust_client.get_project_name()
            print(f"   - Current project name: '{name or 'Untitled'}'")
            
            print(f"   - Setting project name to 'OSC Test Project'...")
            success = rust_client.set_project_name("OSC Test Project")
            print(f"   - Set operation acknowledged: {success}")
            
            time.sleep(0.5)
            
            print("   - Getting project name again...")
            new_name = rust_client.get_project_name()
            print(f"   - Project name after set: '{new_name or 'Untitled'}'")
        
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
            test_name = f"ReaSide Demo {int(time.time())}"
            
            print(f"   - Setting project name to: '{test_name}'")
            project.name = test_name
            
            time.sleep(0.5)
            
            print(f"   - Project name after set via ReaSide: '{project.name}'")
            
            # Restore original name if it wasn't Untitled
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
    print("\nArchitecture:")
    print("- Python sends OSC to Rust extension on port 9877")
    print("- Rust extension calls REAPER API directly")
    print("- Rust extension sends OSC responses back to sender's port")
    print("- ReaSide automatically uses Rust OSC when available")
    print("=" * 60)

if __name__ == "__main__":
    main()