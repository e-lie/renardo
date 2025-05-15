
"""
Test script for REAPER integration with Renardo.

This script provides examples of how to interact with REAPER using the Renardo integration.
The core functionality has been moved to renardo.reaper_backend.reaper_mgt.launcher.
"""
import time

# Import the REAPER management functions from their new location
from renardo.reaper_backend.reaper_mgt.launcher import (
    launch_reaper_with_pythonhome,
    initialize_reapy,
    reinit_reaper_with_backup
)


# Test code
if __name__ == "__main__":
    print("REAPER Integration Test Script")
    print("-----------------------------")
    print("This script demonstrates various ways to interact with REAPER")
    print("The main functionality has been moved to renardo.reaper_backend.reaper_mgt.launcher")
    print("")
    print("Available functions:")
    print("1. Launch REAPER with correct PYTHONHOME")
    print("2. Backup and reinitialize REAPER config")
    print("3. Full Reapy initialization process")
    print("4. Basic Reapy test")
    print("0. Exit")

    while True:
        choice = input("\nEnter your choice (0-4): ")

        if choice == "0":
            print("Exiting...")
            break

        elif choice == "1":
            print("\nLaunching REAPER with correct PYTHONHOME...")
            launch_reaper_with_pythonhome()

        elif choice == "2":
            print("\nBacking up and reinitializing REAPER configuration...")
            reinit_reaper_with_backup()

        elif choice == "3":
            print("\nStarting full Reapy initialization process...")
            success = initialize_reapy()
            print(f"Reapy initialization {'successful' if success else 'failed'}")

        elif choice == "4":
            print("\nTesting basic Reapy functionality...")
            try:
                import reapy

                # Get the current project
                project = reapy.Project()
                print(f"Current project: {project}")

                # Add a test track
                track = project.add_track(index=0, name="Test Track")
                print(f"Successfully created track: {track.name}")

                # Display project info
                print(f"Number of tracks: {len(project.tracks)}")

            except Exception as e:
                print(f"Error in basic Reapy test: {e}")
                print("Make sure REAPER is running and properly configured with Reapy")

        else:
            print("Invalid choice. Please enter a number between 0 and 4.")

    print("\nTest script completed.")
    
    """
    # Additional testing code if needed
    
    from renardo.runtime import *
    
    from renardo.reaper_backend.ReaperIntegration import init_reapy_project, ReaperInstrumentFactory
    
    old_style_presets = {}
    
    reaproject = init_reapy_project()
    
    reainstru_factory = ReaperInstrumentFactory(old_style_presets, reaproject)
    
    add_multiple_fxchains = reainstru_factory.add_multiple_fxchains
    instanciate = reainstru_factory.instanciate
    
    gone = instanciate("chan1", "pads/gone_1")
    # gonec = instanciate("chan1", "effects/limit2_0")
    # bass303 = instanciate("chan2", "bass/bass303_2")
    # bass303c = instanciate("chan2", "effects/limit2_0")
    
    g1 = Player()
    g1 >> gone(0)
    """