"""
Test the reaside server FX chain functionality directly.
"""

import pytest
from pathlib import Path
import tempfile
import time

from renardo.reaper_backend.reaside.core.reaper import Reaper
from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient


def test_server_running():
    """Test if reaside server is running and responding."""
    client = ReaperClient()
    
    # Check server status
    is_running = client.is_server_running()
    print(f"Server running: {is_running}")
    
    if not is_running:
        try:
            client.activate_reaside_server()
            time.sleep(1.0)
            is_running = client.is_server_running()
            print(f"Server running after activation: {is_running}")
        except Exception as e:
            print(f"Server activation failed: {e}")
    
    # Test basic function call
    try:
        version = client.call_reascript_function("GetAppVersion")
        print(f"REAPER version: {version}")
        return True
    except Exception as e:
        print(f"Function call failed: {e}")
        return False


def test_server_fxchain_functions():
    """Test server-side FX chain functions directly."""
    client = ReaperClient()
    reaper = Reaper(client)
    
    # Test server functionality first
    if not test_server_running():
        pytest.skip("Reaside server not running or not functional")
    
    # Get current project and add a track
    project = reaper.current_project
    track = project.add_track()
    track.name = "Server FX Chain Test"
    
    print(f"Created track: {track.name} (index: {track.index})")
    
    # Add some FX
    success1 = track.add_fx("ReaEQ")
    success2 = track.add_fx("ReaComp")
    
    print(f"Added ReaEQ: {success1}, ReaComp: {success2}")
    
    fx_count = track.get_fx_count()
    print(f"FX count: {fx_count}")
    
    if fx_count == 0:
        pytest.skip("No FX were added - cannot test FX chain functionality")
    
    # Test save_fxchain function directly with server
    print("\n=== Testing save_fxchain server function ===")
    
    with tempfile.NamedTemporaryFile(suffix='.RfxChain', delete=False) as temp_file:
        temp_path = Path(temp_file.name)
    
    try:
        # Create request for save
        save_request = {
            "track_index": track.index,
            "file_path": str(temp_path)
        }
        
        # Send request
        client.set_ext_state("reaside", "save_fxchain_request", save_request)
        print(f"Sent save request: {save_request}")
        
        # Wait and check result
        time.sleep(0.5)
        result = client.get_ext_state("reaside", "save_fxchain_result")
        print(f"Save result: {result}")
        print(f"Save result type: {type(result)}")
        
        # Check if file was created
        file_exists = temp_path.exists()
        file_size = temp_path.stat().st_size if file_exists else 0
        print(f"File exists: {file_exists}, size: {file_size}")
        
        if file_exists and file_size > 0:
            with open(temp_path, 'r') as f:
                content = f.read()
            print(f"File content preview: {content[:200]}...")
            
            # Test add_fxchain function
            print("\n=== Testing add_fxchain server function ===")
            
            # Clear the track
            track.delete()
            
            # Create a new clean track
            new_track = project.add_track()
            new_track.name = "Clean Test Track"
            print(f"Created clean track: {new_track.name} (index: {new_track.index})")
            
            initial_fx_count = new_track.get_fx_count()
            print(f"Initial FX count: {initial_fx_count}")
            
            # Create request for add
            add_request = {
                "track_index": new_track.index,
                "file_path": str(temp_path)
            }
            
            # Send request
            client.set_ext_state("reaside", "add_fxchain_request", add_request)
            print(f"Sent add request: {add_request}")
            
            # Wait and check result
            time.sleep(0.5)
            add_result = client.get_ext_state("reaside", "add_fxchain_result")
            print(f"Add result: {add_result}")
            print(f"Add result type: {type(add_result)}")
            
            # Check final FX count
            final_fx_count = new_track.get_fx_count()
            print(f"Final FX count: {final_fx_count}")
            
            if isinstance(add_result, dict) and add_result.get("success"):
                print("✅ FX chain cycle completed successfully!")
            else:
                print("❌ FX chain add failed or returned unexpected result")
        else:
            print("❌ FX chain save failed - no file created or empty file")
    
    finally:
        # Cleanup
        try:
            if temp_path.exists():
                temp_path.unlink()
        except:
            pass


if __name__ == "__main__":
    test_server_fxchain_functions()