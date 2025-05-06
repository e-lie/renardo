"""
SuperCollider management module for RenardoApp

This module provides functionality for managing SuperCollider instances
and file operations related to SuperCollider.
"""

from .sc_classes_files import (
    write_sc_renardo_files_in_user_config,
    is_renardo_sc_classes_initialized,
    SC_USER_CONFIG_DIR,
    SC_USER_EXTENSIONS_DIR
)

from .sclang_instances_mgt import SupercolliderInstance