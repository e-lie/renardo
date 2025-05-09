"""
Renardo application main module

This module contains the main application class (RenardoApp), the StateManager class,
and the SuperCollider management submodule.

The StateManager is designed to replace the state_service module with a more
object-oriented approach to state management.
"""

from .state_manager import StateManager
from .renardo_app import RenardoApp

# Make sure the singleton is easily accessible
get_instance = RenardoApp.get_instance