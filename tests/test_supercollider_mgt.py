"""
Tests for the supercollider_mgt module
"""
import pytest
from unittest.mock import patch, MagicMock

from renardo.renardo_app.supercollider_mgt import (
    SupercolliderInstance,
    is_renardo_sc_classes_initialized,
    SC_USER_CONFIG_DIR
)


def test_sc_user_config_dir_exists():
    """Test that SuperCollider user config directory is defined"""
    assert SC_USER_CONFIG_DIR is not None


@patch('renardo.renardo_app.supercollider_mgt.sc_classes_files.Path.exists')
def test_is_renardo_sc_classes_initialized(mock_exists):
    """Test the is_renardo_sc_classes_initialized function"""
    # Set up mock to return True for all Path.exists calls
    mock_exists.return_value = True
    
    # Test function
    result = is_renardo_sc_classes_initialized()
    
    # Verify result
    assert result is True
    
    # Test when files don't exist
    mock_exists.return_value = False
    result = is_renardo_sc_classes_initialized()
    assert result is False


@patch('renardo.renardo_app.supercollider_mgt.sclang_instances_mgt.subprocess')
def test_supercollider_instance_initialization(mock_subprocess):
    """Test the SupercolliderInstance class initialization"""
    # Set up mock
    mock_subprocess.run.return_value = MagicMock(returncode=0)
    
    # Create instance
    sc_instance = SupercolliderInstance()
    
    # Verify instance attributes
    assert sc_instance.sclang_process is None
    assert hasattr(sc_instance, 'sclang_exec')
    assert hasattr(sc_instance, 'check_exec')