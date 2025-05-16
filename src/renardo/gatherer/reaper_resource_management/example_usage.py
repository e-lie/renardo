#!/usr/bin/env python
"""
Example usage of the Reaper resource management system.
"""

from pathlib import Path
from renardo.gatherer.reaper_resource_management.reaper_resource_library import ReaperResourceLibrary
from renardo.lib.music_resource import ResourceType


def main():
    # Example directory structure:
    # reaper_resources/
    #   0_basic_resources/
    #     instruments/
    #       bass/
    #         massive_bass.py
    #         serum_bass.py
    #       lead/
    #         analog_lead.py
    #     effects/
    #       reverb/
    #         pro_r.py
    #       delay/
    #         h_delay.py
    
    # Create a library from a root directory
    library_path = Path("/path/to/reaper_resources")
    library = ReaperResourceLibrary(library_path)
    
    # List all banks
    print("Available plugin banks:")
    for bank_name in library.list_banks():
        print(f"  {bank_name}")
    
    # Get a specific bank
    bank = library.get_bank(0)
    if bank:
        print(f"\nBank: {bank.name}")
        
        print("\nInstrument categories:")
        for category in bank.instruments:
            print(f"  {category.category}")
            for plugin in category:
                print(f"    {plugin}")
        
        print("\nEffect categories:")
        for category in bank.effects:
            print(f"  {category.category}")
            for plugin in category:
                print(f"    {plugin}")
        
        # Get a specific instrument
        bass = bank.get_resource(ResourceType.INSTRUMENT, "bass", "massive_bass")
        if bass:
            print(f"\nFound instrument: {bass}")
            # Load the actual resource
            resource = bass.load_resource_from_python()
            if resource:
                print(f"Loaded resource: {resource.name}")
        
        # Get a specific effect
        reverb = bank.get_resource(ResourceType.EFFECT, "reverb", "pro_r")
        if reverb:
            print(f"\nFound effect: {reverb}")


if __name__ == "__main__":
    main()