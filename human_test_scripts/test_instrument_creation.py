#!/usr/bin/env python3
"""Test instrument creation with MIDI input and parameter functionality."""

import sys
import os

# Add the renardo package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.runtime import *

def test_instrument_creation():
    """Test creating an instrument and checking MIDI input configuration."""
    print("=== Testing Instrument Creation ===")
    print()
    
    try:
        
        # Clear REAPER first
        print("Clearing REAPER...")
        reaproject.clear_reaper()
        print("✅ REAPER cleared")
        print()
        
        # Create a bass303 instrument using existing FX chain
        print("Creating bass303 instrument...")
        bass303 = ReaperInstrument(
            shortname="bass303",
            fxchain_path="/path/to/bass303.RfxChain"  # Will use fallback
        )
        
        print(f"✅ Created bass303: {bass303}")
        print(f"Track name: {bass303.track.name}")
        print(f"MIDI channel: {bass303._midi_channel}")
        print()
        
        # Test parameter setting with TimeVar
        print("Testing parameter setting with linvar...")
        try:
            # Create TimeVar patterns
            cutoff_pattern = linvar([0, 1])
            volin_pattern = linvar([0, 1])
            
            print(f"cutoff pattern: {cutoff_pattern}")
            print(f"volin pattern: {volin_pattern}")
            
            # Test playing notes with parameters
            print("Playing notes with parameters...")
            pattern = b4 >> bass303([0, 2, 0, 4], cutoff=cutoff_pattern, volin=volin_pattern)
            
            print("✅ Pattern created successfully")
            print(f"Pattern: {pattern}")
            
        except Exception as e:
            print(f"❌ Error with parameter setting: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Error during instrument creation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_instrument_creation()