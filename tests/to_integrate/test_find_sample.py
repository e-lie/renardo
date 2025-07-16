# SPDX-FileCopyrightText: 2024-present Elie Gavoty <mail@eliegavoty.fr>
#
# SPDX-License-Identifier: MIT



# def test_get_reaper_track_names():
#     track_names = get_reaper_track_names()
#     assert isinstance(track_names, list), "Track names should be a list"

import pytest
from pathlib import Path
import tempfile
import shutil
from renardo.sc_backend import BufferManager


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
def buffer_manager(sample_dir):
    """Create a BufferManager instance configured with the sample directory."""
    bm = BufferManager()
    bm._paths = [sample_dir['root']]
    return bm


def test_abspath(buffer_manager, sample_dir):
    """Test finding sample file using absolute path."""
    sample = str(sample_dir['yeah'])
    found = buffer_manager._find_sample(sample)
    assert found == sample


def test_abspath_no_ext(buffer_manager, sample_dir):
    """Test finding sample file using absolute path without extension."""
    sample = str(sample_dir['yeah'].with_suffix(''))
    found = buffer_manager._find_sample(sample)
    assert found == str(sample_dir['yeah'])


def test_relpath(buffer_manager, sample_dir):
    """Test finding sample file using relative path."""
    found = buffer_manager._find_sample('yeah.wav')
    assert found == str(sample_dir['yeah'])


def test_relpath_no_ext(buffer_manager, sample_dir):
    """Test finding sample file using relative path without extension."""
    found = buffer_manager._find_sample('yeah')
    assert found == str(sample_dir['yeah'])


def test_dir_first(buffer_manager, sample_dir):
    """Test loading first sample from directory."""
    found = buffer_manager._find_sample('snares')
    assert found == str(sample_dir['snare1'])


def test_dir_nth(buffer_manager, sample_dir):
    """Test loading nth sample from directory."""
    found = buffer_manager._find_sample('snares', 1)
    assert found == str(sample_dir['snare2'])


def test_dir_nth_overflow(buffer_manager, sample_dir):
    """Test loading nth sample from directory when n exceeds file count."""
    found = buffer_manager._find_sample('snares', 2)
    assert found == str(sample_dir['snare1'])


def test_nested_filename(buffer_manager, sample_dir):
    """Test finding sample by filename in nested directory."""
    found = buffer_manager._find_sample('snare1.wav')
    assert found == str(sample_dir['snare1'])


def test_nested_filename_no_ext(buffer_manager, sample_dir):
    """Test finding sample by filename without extension in nested directory."""
    found = buffer_manager._find_sample('snare1')
    assert found == str(sample_dir['snare1'])


def test_pathpattern(buffer_manager, sample_dir):
    """Test finding sample using path pattern."""
    found = buffer_manager._find_sample('k?c*/*')
    assert found == str(sample_dir['808'])


def test_pathpattern_doublestar(buffer_manager, sample_dir):
    """Test finding sample using pattern with double asterisk."""
    found = buffer_manager._find_sample('**/snare*')
    assert found == str(sample_dir['snare1'])


def test_doublestar_deep_path(buffer_manager, sample_dir):
    """Test finding sample in deep path using double asterisk."""
    found = buffer_manager._find_sample('**/house/*')
    assert found == str(sample_dir['house_kick'])