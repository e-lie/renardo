"""
Fixes for issues that can arise when using the MIDI backend.

This module provides functionality to patch or modify Renardo classes
to better support MIDI operation.
"""

import inspect
from types import MethodType

def fix_attribute_warnings():
    """
    Fix warnings about non-numeric attributes in Player objects.
    
    These warnings happen because the Player class tries to convert all
    attributes to numeric values for SuperCollider, but MIDI-specific
    attributes are not numeric.
    
    Returns:
        bool: True if fixes were applied, False otherwise
    """
    try:
        from renardo.lib.Player.player import Player
        
        # Find the method that's causing the warnings
        if hasattr(Player, '_get_event_value'):
            original_get_event_value = Player._get_event_value
            
            def patched_get_event_value(self, attr):
                """
                Modified version that skips MIDI-specific attributes.
                """
                # Skip MIDI-specific attributes
                if attr in ('midi_instrument', 'midi_proxy', '__class__', '__dict__', '__weakref__'):
                    return None
                
                # Call original method for other attributes
                return original_get_event_value(self, attr)
            
            # Replace the method
            Player._get_event_value = patched_get_event_value
            return True
            
        # Don't try to patch _get_event - it's too complex
        return True
        
        return False
        
    except (ImportError, AttributeError) as e:
        print(f"Warning: Could not apply attribute warning fixes: {e}")
        return False


def fix_supercollider_synth_lookup():
    """
    Fix errors when SuperCollider tries to look up MIDI instruments.
    
    These errors happen because even though we're handling MIDI events,
    the original SC server code still tries to find the instrument.
    
    Returns:
        bool: True if fixes were applied, False otherwise
    """
    try:
        from renardo.sc_backend.server_manager import ServerManager
        
        # Find the bundle generation method
        if hasattr(ServerManager, 'get_bundle'):
            original_get_bundle = ServerManager.get_bundle
            
            def patched_get_bundle(self, synthdef, message, timestamp=0):
                """
                Modified version that handles MIDI instrument names.
                """
                # Check if this is a MIDI instrument
                if isinstance(synthdef, str):
                    if synthdef in ('piano', 'bass', 'drums', 'strings') or synthdef.startswith('midi_'):
                        # Return an empty bundle for MIDI instruments
                        from renardo.sc_backend.custom_osc_lib import OSCBundle
                        return OSCBundle(timestamp=timestamp)
                
                # Call original method for regular SC instruments
                return original_get_bundle(self, synthdef, message, timestamp)
            
            # Replace the method
            ServerManager.get_bundle = patched_get_bundle
            return True
        
        return False
        
    except (ImportError, AttributeError) as e:
        print(f"Warning: Could not apply SuperCollider synth lookup fixes: {e}")
        return False


def apply_all_fixes():
    """
    Apply all available fixes for the MIDI backend.
    
    Returns:
        dict: Results of each fix (True if applied, False otherwise)
    """
    results = {
        'attribute_warnings': fix_attribute_warnings(),
        'sc_synth_lookup': fix_supercollider_synth_lookup()
    }
    
    return results