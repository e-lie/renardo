# SPDX-FileCopyrightText: 2024-present Elie Gavoty <mail@eliegavoty.fr>
#
# SPDX-License-Identifier: MIT

import pytest
from pathlib import Path
import tempfile
import os
from renardo.gatherer.reaper_resource_management.reaper_resource_library import ReaperResourceLibrary


@pytest.fixture
def reaper_resource_dir():
    """Create a temporary directory structure with Reaper resources."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create bank 0_basic_resources
        bank0_dir = root / "0_basic_resources"
        bank0_dir.mkdir()
        
        # Create effects directory and categories within bank 0
        effects0_dir = bank0_dir / "effects"
        effects0_dir.mkdir()
        
        # Create reverb category
        reverb_dir = effects0_dir / "reverb"
        reverb_dir.mkdir()
        
        # Create reverb fx chains
        classic_reverb = reverb_dir / "Classic Reverb.RfxChain"
        classic_reverb.touch()
        
        hall_reverb = reverb_dir / "Hall Reverb.RfxChain"
        hall_reverb.touch()
        
        # Create delay category
        delay_dir = effects0_dir / "delay"
        delay_dir.mkdir()
        
        # Create delay fx chains
        stereo_delay = delay_dir / "Stereo Delay.RfxChain"
        stereo_delay.touch()
        
        # Create bank 1_advanced_resources
        bank1_dir = root / "1_advanced_resources"
        bank1_dir.mkdir()
        
        # Create effects directory and categories within bank 1
        effects1_dir = bank1_dir / "effects"
        effects1_dir.mkdir()
        
        # Create creative category
        creative_dir = effects1_dir / "creative"
        creative_dir.mkdir()
        
        # Create creative fx chains
        weird_delay = creative_dir / "Weird DELAY Effect.RfxChain"
        weird_delay.touch()
        
        # Mixed case to test case-insensitivity
        glitch_reverb = creative_dir / "Glitch REVERB.RfxChain"
        glitch_reverb.touch()
        
        # Create instruments directory and categories within bank 0
        instruments0_dir = bank0_dir / "instruments"
        instruments0_dir.mkdir()
        
        # Create piano category
        piano_dir = instruments0_dir / "piano"
        piano_dir.mkdir()
        
        # Create piano instrument chains
        grand_piano = piano_dir / "Grand Piano.RfxChain"
        grand_piano.touch()
        
        # Create synth category
        synth_dir = instruments0_dir / "synth"
        synth_dir.mkdir()
        
        # Create synth instrument chains
        analog_synth = synth_dir / "Analog Synth.RfxChain"
        analog_synth.touch()

        yield {
            'root': root,
            'classic_reverb': classic_reverb,
            'hall_reverb': hall_reverb,
            'stereo_delay': stereo_delay,
            'weird_delay': weird_delay,
            'glitch_reverb': glitch_reverb,
            'grand_piano': grand_piano,
            'analog_synth': analog_synth
        }


@pytest.fixture
def reaper_resource_lib(reaper_resource_dir):
    """Create a ReaperResourceLibrary instance configured with the temporary directory."""
    root_dir = reaper_resource_dir['root']
    print(f"\nCreating ReaperResourceLibrary with root: {root_dir}")
    lib = ReaperResourceLibrary(root_dir)
    
    # Debug info
    print(f"Banks loaded: {lib.list_banks()}")
    print(f"Bank count: {len(lib._banks)}")
    
    # List the directory structure
    print("\nDirectory structure:")
    for path in root_dir.glob('**/*'):
        if path.is_file():
            print(f"FILE: {path.relative_to(root_dir)}")
        else:
            print(f"DIR: {path.relative_to(root_dir)}")
    
    return lib


def test_find_fxchain_exact_match(reaper_resource_lib, reaper_resource_dir):
    """Test finding fxchain by exact name match."""
    # Test with exact name including extension
    found = reaper_resource_lib.find_fxchain_by_name("Classic Reverb.RfxChain")
    assert found == reaper_resource_dir['classic_reverb']
    
    # Test with exact name without extension
    found = reaper_resource_lib.find_fxchain_by_name("Classic Reverb")
    assert found == reaper_resource_dir['classic_reverb']


def test_find_fxchain_case_insensitive(reaper_resource_lib, reaper_resource_dir):
    """Test finding fxchain with case-insensitive match."""
    # Original is "Glitch REVERB.RfxChain"
    found = reaper_resource_lib.find_fxchain_by_name("glitch reverb.rfxchain")
    assert found == reaper_resource_dir['glitch_reverb']
    
    # Test with different case without extension
    found = reaper_resource_lib.find_fxchain_by_name("GLITCH reverb")
    assert found == reaper_resource_dir['glitch_reverb']


def test_find_fxchain_partial_match(reaper_resource_lib, reaper_resource_dir):
    """Test finding fxchain with partial name match."""
    # "Weird DELAY Effect.RfxChain" should match with partial "delay"
    found = reaper_resource_lib.find_fxchain_by_name("delay")
    assert found == reaper_resource_dir['stereo_delay']  # Should find the first match alphabetically across categories
    
    # Partial match with a more specific term
    found = reaper_resource_lib.find_fxchain_by_name("weird")
    assert found == reaper_resource_dir['weird_delay']


def test_find_fxchain_nonexistent(reaper_resource_lib):
    """Test finding a nonexistent fxchain."""
    found = reaper_resource_lib.find_fxchain_by_name("Nonexistent Effect")
    assert found is None
    
    
def test_find_instrument_fxchain(reaper_resource_lib, reaper_resource_dir):
    """Test finding fxchain in the instruments directory."""
    # Test with exact name including extension
    found = reaper_resource_lib.find_fxchain_by_name("Grand Piano.RfxChain")
    assert found == reaper_resource_dir['grand_piano']
    
    # Test with exact name without extension
    found = reaper_resource_lib.find_fxchain_by_name("Grand Piano")
    assert found == reaper_resource_dir['grand_piano']
    
    # Test partial name match
    found = reaper_resource_lib.find_fxchain_by_name("analog")
    assert found == reaper_resource_dir['analog_synth']