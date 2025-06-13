"""
SuperCollider management module for RenardoApp

This module provides functionality for managing SuperCollider instances
and file operations related to SuperCollider.
"""

from .sc_classes_files import (
    write_sc_renardo_files_in_user_config,
    is_renardo_sc_classes_initialized,
    should_update_renardo_sc_classes,
    SC_USER_CONFIG_DIR,
    SC_USER_EXTENSIONS_DIR
)

from .sclang_instances_mgt import SupercolliderInstance

def ensure_sc_classes_are_current():
    """Ensure SuperCollider classes are up to date, auto-updating if necessary"""
    if should_update_renardo_sc_classes():
        print("SuperCollider classes are outdated, updating automatically...")
        write_sc_renardo_files_in_user_config()
        print("SuperCollider classes (Renardo.sc, StageLimiter.sc, start_renardo.scd) updated successfully.")