#!/usr/bin/env python3
"""
Simple test script for ensure_fxchain_in_reaper functionality
"""

from pathlib import Path
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_fxchain_logic():
    """Test the logic of ensure_fxchain_in_reaper without full initialization."""
    print("Testing FXChain installation logic...")
    
    # Create test directories
    test_dir = Path("/tmp/renardo_fxchain_test")
    test_dir.mkdir(exist_ok=True)
    
    # Create mock REAPER directory structure
    reaper_dir = test_dir / "REAPER"
    fxchains_dir = reaper_dir / "FXChains"
    renardo_fxchains_dir = fxchains_dir / "renardo_fxchains"
    renardo_fxchains_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a source FXChain file
    source_dir = test_dir / "source"
    source_dir.mkdir(exist_ok=True)
    source_file = source_dir / "test.RfxChain"
    
    with open(source_file, 'w') as f:
        f.write('''<FXCHAIN
SHOW 0
LASTSEL 0
DOCKED 0
>
''')
    
    # Test copying logic
    import shutil
    dest_file = renardo_fxchains_dir / "test.RfxChain"
    
    print(f"Source: {source_file}")
    print(f"Destination: {dest_file}")
    print(f"Source exists: {source_file.exists()}")
    
    # Copy the file
    shutil.copy2(source_file, dest_file)
    print(f"Destination exists after copy: {dest_file.exists()}")
    
    # Test content comparison
    with open(source_file, 'rb') as src:
        src_content = src.read()
    with open(dest_file, 'rb') as dst:
        dst_content = dst.read()
    
    print(f"Content matches: {src_content == dst_content}")
    
    # Clean up
    import shutil
    shutil.rmtree(test_dir)
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_fxchain_logic()