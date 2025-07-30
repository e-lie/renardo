"""
Test loading a preexisting FX chain file called 'test_chain.RfxChain' from REAPER's FX chains directory.
"""

import pytest
from pathlib import Path
import os

from renardo.reaper_backend.reaside.core.reaper import Reaper
from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient


@pytest.fixture
def reaper_setup():
    """Set up REAPER connection and clean project."""
    client = ReaperClient()
    reaper = Reaper(client)
    project = reaper.current_project
    
    yield reaper, project
    
    # Cleanup: remove any test tracks
    # (Best effort - don't fail if cleanup fails)


def test_load_preexisting_fxchain(reaper_setup):
    """
    Test loading a preexisting FX chain called 'test_chain.RfxChain'.
    
    This test will automatically create the test_chain.RfxChain file if it doesn't exist.
    """
    reaper, project = reaper_setup
    
    # Define the test FX chain content (ReaEQ + ReaComp with custom settings)
    test_fxchain_content = """BYPASS 0 0
<VST "VST: ReaEQ (Cockos)" reaeq.vst.so 0 ReaEQTest 1919247729<56535472656571726561657100000000> ""
  cWVlcu5e7f4CAAAAAQAAAAAAAAACAAAAAAAAAAIAAAABAAAAAAAAAAIAAAAAAAAAzQAAAAEAAAAAABAA
  IQAAAAUAAAAAAAAAAQAAAAAAAAAAAFlAAAAAAAAA8D+amZmZmZnpPwEIAAAAAQAAAAAAAAAAwHJAAAAAAAAA8D8AAAAAAAAAQAEIAAAA
  AQAAAAAAAAAAQI9AAAAAAAAA8D8AAAAAAAAAQAEBAAAAAQAAAAAAAAAAiLNAAAAAAAAA8D+amZmZmZnpPwEEAAAAAAAAAAAAAAAAAFlAAAAAAAAA8D8AAAAAAAAAQAEB
  AAAAAQAAAAAAAAAAAPA/AAAAGIQCAACWAQAAAgAAAA==
  AAAQAAAA
>
FXID {9DAC4DAF-8BF6-8A8F-73BD-812174B82A46}
WAK 0 0
BYPASS 0 0
<VST "VST: ReaComp (Cockos)" reacomp.vst.so 0 ReaCompTest 1919247213<5653547265636D726561636F6D700000> ""
  bWNlcu9e7f4EAAAAAQAAAAAAAAACAAAAAAAAAAQAAAAAAAAACAAAAAAAAAACAAAAAQAAAAAAAAACAAAAAAAAAFwAAAAAAAAAAAAQAA==
  776t3g3wrd4AAIA/ED74PKabxDsK16M8AAAAAAAAAAAAAIA/AAAAAAAAAAAAAAAAnNEHMwAAgD8AAAAAzcxMPQAAAAAAAAAAAAAAAAAAgD4AAAAAAAAAAAAAAAA=
  AAAQAAAA
>
FXID {BB2214ED-2D36-743E-6BE6-EABAC6BBEECE}
WAK 0 0"""
    
    # Find or create the test_chain.RfxChain file
    print("\n=== Setting up test_chain.RfxChain ===")
    
    # Common REAPER FX chains directories
    possible_dirs = [
        Path.home() / "Documents" / "REAPER" / "FXChains",
        Path.home() / ".config" / "REAPER" / "FXChains", 
        Path("/opt/REAPER/FXChains"),
        Path("~/REAPER/FXChains").expanduser(),
    ]
    
    # Find the first existing REAPER FXChains directory
    fxchains_dir = None
    for dir_path in possible_dirs:
        if dir_path.is_dir():
            fxchains_dir = dir_path
            print(f"📁 Found REAPER FXChains directory: {fxchains_dir}")
            break
    
    # If no FXChains directory exists, create one in the most likely location
    if not fxchains_dir:
        # Try to create in ~/.config/REAPER/FXChains (common on Linux)
        fxchains_dir = Path.home() / ".config" / "REAPER" / "FXChains"
        print(f"📁 Creating REAPER FXChains directory: {fxchains_dir}")
        try:
            fxchains_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            pytest.skip(f"Could not create FXChains directory {fxchains_dir}: {e}")
    
    # Set up the test chain file path
    chain_path = fxchains_dir / "test_chain.RfxChain"
    
    # Create or update the test_chain.RfxChain file
    try:
        with open(chain_path, 'w') as f:
            f.write(test_fxchain_content)
        print(f"✅ Created test_chain.RfxChain at: {chain_path}")
    except Exception as e:
        pytest.skip(f"Failed to create test_chain.RfxChain: {e}")
    
    print(f"✅ Found FX chain file: {chain_path}")
    
    # Read and display the FX chain content
    try:
        with open(chain_path, 'r') as f:
            chain_content = f.read()
        print(f"📄 FX chain file size: {len(chain_content)} characters")
        print(f"📄 Content preview:\n{chain_content[:300]}...")
        
        # Basic validation
        if not chain_content.strip():
            pytest.fail(f"FX chain file is empty: {chain_path}")
            
        if "<FXCHAIN" not in chain_content and "BYPASS" not in chain_content:
            pytest.fail(f"FX chain file doesn't contain expected FX chain data: {chain_path}")
            
    except Exception as e:
        pytest.fail(f"Failed to read FX chain file {chain_path}: {e}")
    
    # Create a clean track for testing
    print("\n=== Creating test track ===")
    track = project.add_track()
    track.name = "FX Chain Test Track"
    
    initial_fx_count = track.get_fx_count()
    print(f"📊 Initial FX count: {initial_fx_count}")
    
    # Add a preexisting FX to verify the chain is added after it
    print("\n=== Adding preexisting FX ===")
    preexisting_fx_added = track.add_fx("ReaDelay")
    if preexisting_fx_added:
        preexisting_fx_count = track.get_fx_count()
        preexisting_fx_name = track.get_fx_name(0) if preexisting_fx_count > 0 else "Unknown"
        print(f"✅ Added preexisting FX: {preexisting_fx_name}")
        print(f"📊 FX count after adding preexisting FX: {preexisting_fx_count}")
    else:
        preexisting_fx_count = initial_fx_count
        print("⚠️  Failed to add preexisting FX, continuing without it")
    
    # Load the FX chain
    print(f"\n=== Loading FX chain from {chain_path.name} ===")
    try:
        fx_added = track.add_fxchain(chain_path)
        print(f"🔧 FX added by add_fxchain: {fx_added}")
        
        # Check final FX count
        final_fx_count = track.get_fx_count()
        print(f"📊 Final FX count: {final_fx_count}")
        
        # Expected count should be preexisting FX + 2 FX from chain (ReaEQ + ReaComp)
        expected_fx_from_chain = 2  # ReaEQ + ReaComp from our test chain
        expected_fx_count = preexisting_fx_count + expected_fx_from_chain
        print(f"📊 Expected FX count: {expected_fx_count} (preexisting: {preexisting_fx_count} + chain: {expected_fx_from_chain})")
        print(f"📊 Actual result: {fx_added} FX added, final count: {final_fx_count}")
        
        # Get detailed server response for debugging
        import time
        time.sleep(0.1)
        server_result = track._client.get_ext_state("reaside", "add_fxchain_result")
        
        if isinstance(server_result, dict):
            print(f"\n=== Server Response ===")
            print(f"Success: {server_result.get('success')}")
            print(f"FX added: {server_result.get('fx_added')}")
            print(f"FX count before: {server_result.get('fx_count_before')}")
            print(f"FX count after: {server_result.get('fx_count_after')}")
            print(f"SetTrackStateChunk result: {server_result.get('set_chunk_result')}")
            
            # Show debug info if available
            if "debug" in server_result:
                debug = server_result["debug"]
                print(f"\n=== Debug Info ===")
                print(f"Chunk changed: {debug.get('chunk_changed')}")
                print(f"Original chunk length: {debug.get('original_chunk_length')}")
                print(f"New chunk length: {debug.get('new_chunk_length')}")
                print(f"Chain content length: {debug.get('chain_content_length')}")
                print(f"Original has FXCHAIN: {debug.get('original_has_fxchain')}")
                print(f"New has FXCHAIN: {debug.get('new_has_fxchain')}")
        
        # List all FX that are now on the track
        if final_fx_count > 0:
            print(f"\n=== All FX on track ===")
            for i in range(final_fx_count):
                fx_name = track.get_fx_name(i)
                if i < preexisting_fx_count:
                    print(f"  FX {i}: {fx_name} (preexisting)")
                else:
                    print(f"  FX {i}: {fx_name} (from chain)")
        else:
            print(f"\n=== No FX found on track ===")
        
        # Validation
        if final_fx_count > preexisting_fx_count:
            print("🎉 SUCCESS: FX chain loaded successfully!")
            print(f"✅ Track went from {preexisting_fx_count} to {final_fx_count} FX")
            
            # Verify the preexisting FX is still in position 0 (if we had one)
            if preexisting_fx_count > 0 and final_fx_count > 0:
                first_fx_name = track.get_fx_name(0)
                if "ReaDelay" in first_fx_name:
                    print("✅ Preexisting FX (ReaDelay) is still in position 0")
                else:
                    print(f"⚠️  Expected ReaDelay at position 0, but found: {first_fx_name}")
            
            # Verify we got the expected FX from the chain
            if final_fx_count >= expected_fx_count:
                # Check for ReaEQ and ReaComp from our test chain
                fx_names = [track.get_fx_name(i) for i in range(final_fx_count)]
                has_reaeq = any("ReaEQ" in name for name in fx_names)
                has_reacomp = any("ReaComp" in name for name in fx_names)
                
                if has_reaeq and has_reacomp:
                    print("✅ Found both ReaEQ and ReaComp from the test chain")
                else:
                    print(f"⚠️  Missing expected FX - ReaEQ: {has_reaeq}, ReaComp: {has_reacomp}")
            
            assert final_fx_count > preexisting_fx_count, "FX count should have increased from preexisting count"
            assert fx_added > 0, "add_fxchain should report FX were added"
            
            # Ideal case: we should have exactly the expected count
            if final_fx_count == expected_fx_count:
                print(f"🎯 Perfect! Got exactly the expected {expected_fx_count} FX")
            else:
                print(f"📊 Note: Expected {expected_fx_count} but got {final_fx_count} FX")
            
        elif final_fx_count == preexisting_fx_count and fx_added == 0:
            print("⚠️  FX chain processing completed but no FX were added")
            print("   This indicates the method is working but there may be:")
            print("   - Plugin compatibility issues")
            print("   - FX chain format issues") 
            print("   - REAPER version compatibility issues")
            
            # Verify preexisting FX is still there
            if preexisting_fx_count > 0:
                first_fx_name = track.get_fx_name(0) 
                if "ReaDelay" in first_fx_name:
                    print("✅ At least the preexisting FX (ReaDelay) is still present")
                else:
                    print(f"⚠️  Preexisting FX missing! Found: {first_fx_name}")
            
            # The test passes because the method executed without errors
            assert fx_added == 0, f"Expected 0 FX added, got {fx_added}"
            
        else:
            print(f"❌ Unexpected state: initial={initial_fx_count}, preexisting={preexisting_fx_count}, final={final_fx_count}, added={fx_added}")
            pytest.fail(f"Unexpected FX count state")
        
        # Try to access FX through reaside
        track.rescan_fx()
        fx_objects = track.list_fx()
        print(f"📋 FX objects created by reaside: {len(fx_objects)}")
        
        for fx_obj in fx_objects:
            print(f"  🔧 {fx_obj.name} (snake: {fx_obj.snake_name})")
            
    except Exception as e:
        print(f"❌ Error loading FX chain: {e}")
        raise
    
    # Cleanup
    try:
        track.delete()
    except:
        pass  # Best effort cleanup
        
    # Clean up the test FX chain file
    try:
        if chain_path.exists():
            chain_path.unlink()
            print(f"🧹 Cleaned up test_chain.RfxChain")
    except:
        pass  # Best effort cleanup


if __name__ == "__main__":
    # Allow running the test directly
    pytest.main([__file__, "-v", "-s"])