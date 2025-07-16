# SPDX-FileCopyrightText: 2024-present Elie Gavoty <mail@eliegavoty.fr>
#
# SPDX-License-Identifier: MIT

import pytest
from pathlib import Path
import tempfile
from renardo.gatherer import SamplePackLibrary
from renardo.settings_manager import settings

@pytest.fixture
def sample_dir():
    """Create a temporary directory structure with sample files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create root level sample
        yeah = root / "yeah.wav"
        yeah.touch()

        # Create snares directory and samples
        snares = root / "snares"
        snares.mkdir()
        snare1 = snares / "snare1.wav"
        snare2 = snares / "snare2.wav"
        snare1.touch()
        snare2.touch()

        # Create kicks directory and samples
        kicks = root / "kicks"
        kicks.mkdir()
        kick808 = kicks / "808.wav"
        kick = kicks / "kick.wav"
        kick808.touch()
        kick.touch()

        # Create nested house kicks
        house = kicks / "house"
        house.mkdir()
        house_kick = house / "house_bass.wav"
        house_kick.touch()

        yield {
            'root': root,
            'yeah': yeah,
            'snare1': snare1,
            'snare2': snare2,
            '808': kick808,
            'kick': kick,
            'house_kick': house_kick
        }

@pytest.fixture
def sample_pack_lib(sample_dir):
    """Create a Sample Pack Library instance configured with the sample directory."""
    spack_lib = SamplePackLibrary(
        root_directory=settings.get_path("SAMPLES_DIR"),
        extra_paths=[sample_dir['root']]
    )
    return spack_lib

def test_abspath(sample_pack_lib, sample_dir):
    """Test finding sample file using absolute path."""
    sample = str(sample_dir['yeah'])
    found = sample_pack_lib._find_sample(sample)
    assert found is not None
    assert found.path == sample_dir['yeah']
    assert found.index == 0

def test_abspath_no_ext(sample_pack_lib, sample_dir):
    """Test finding sample file using absolute path without extension."""
    sample = str(sample_dir['yeah'].with_suffix(''))
    found = sample_pack_lib._find_sample(sample)
    assert found is not None
    assert found.path == sample_dir['yeah']

def test_relpath(sample_pack_lib, sample_dir):
    """Test finding sample file using relative path."""
    found = sample_pack_lib._find_sample('yeah.wav')
    assert found is not None
    assert found.path == sample_dir['yeah']

def test_relpath_no_ext(sample_pack_lib, sample_dir):
    """Test finding sample file using relative path without extension."""
    found = sample_pack_lib._find_sample('yeah')
    assert found is not None
    assert found.path == sample_dir['yeah']

def test_dir_first(sample_pack_lib, sample_dir):
    """Test loading first sample from directory."""
    found = sample_pack_lib._find_sample('snares')
    assert found is not None
    assert found.path == sample_dir['snare1']
    assert found.category == "snares"
    assert found.index == 0

def test_dir_nth(sample_pack_lib, sample_dir):
    """Test loading nth sample from directory."""
    found = sample_pack_lib._find_sample('snares', 1)
    assert found is not None
    assert found.path == sample_dir['snare2']
    assert found.category == "snares"
    assert found.index == 1

def test_dir_nth_overflow(sample_pack_lib, sample_dir):
    """Test loading nth sample from directory when n exceeds file count."""
    found = sample_pack_lib._find_sample('snares', 2)
    assert found is not None
    assert found.path == sample_dir['snare1']
    assert found.category == "snares"
    assert found.index == 2

def test_nested_filename(sample_pack_lib, sample_dir):
    """Test finding sample by filename in nested directory."""
    found = sample_pack_lib._find_sample('snare1.wav')
    assert found is not None
    assert found.path == sample_dir['snare1']
    assert found.category == "snares"

def test_nested_filename_no_ext(sample_pack_lib, sample_dir):
    """Test finding sample by filename without extension in nested directory."""
    found = sample_pack_lib._find_sample('snare1')
    assert found is not None
    assert found.path == sample_dir['snare1']
    assert found.category == "snares"

def test_pathpattern(sample_pack_lib, sample_dir):
    """Test finding sample using path pattern."""
    found = sample_pack_lib._find_sample('k?c*/*')
    assert found is not None
    assert found.path == sample_dir['808']
    assert found.category == "kicks"

def test_pathpattern_doublestar(sample_pack_lib, sample_dir):
    """Test finding sample using pattern with double asterisk."""
    found = sample_pack_lib._find_sample('**/snare*')
    assert found is not None
    assert found.path == sample_dir['snare1']
    assert found.category == "snares"

def test_doublestar_deep_path(sample_pack_lib, sample_dir):
    """Test finding sample in deep path using double asterisk."""
    found = sample_pack_lib._find_sample('**/house/*')
    assert found is not None
    assert found.path == sample_dir['house_kick']
    assert found.category == "house"
