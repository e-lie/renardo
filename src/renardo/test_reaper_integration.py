
import os
import subprocess
import sys
import os.path
import time
from pathlib import Path

from renardo.reaper_backend.reaper_mgt.shared_library import get_python_shared_library


def launch_reaper_with_pythonhome():
    """
    Launch REAPER.app on macOS with the correct PYTHONHOME environment variable.
    
    This function:
    1. Uses get_python_shared_library to find the current Python library path
    2. Extracts the Python home directory from the library path
    3. Sets PYTHONHOME environment variable to point to the current Python installation
    4. Launches the REAPER application from /Applications/REAPER.app
    """
    try:
        # Get the Python shared library path
        python_lib_path = get_python_shared_library()
        print(f"Python shared library found at: {python_lib_path}")
        
        # Extract the Python home directory from the library path
        # Typical path would be something like /path/to/python/lib/libpython3.x.dylib
        # We need to remove the /lib/libpython3.x.dylib part
        if "lib/libpython" in python_lib_path:
            python_home = python_lib_path.split("lib/libpython")[0]
        else:
            # Fallback to a reasonable guess if the expected pattern isn't found
            python_home = str(Path(sys.executable).parent.parent)
        
        print(f"Setting PYTHONHOME to: {python_home}")
        
        # Prepare environment with PYTHONHOME set
        env = os.environ.copy()
        env["PYTHONHOME"] = python_home
        
        # Path to REAPER application on macOS
        reaper_path = "/Applications/REAPER.app/Contents/MacOS/REAPER"
        
        if not os.path.exists(reaper_path):
            print(f"Error: REAPER application not found at {reaper_path}")
            return False
        
        # Launch REAPER with the modified environment
        print(f"Launching REAPER from: {reaper_path}")
        process = subprocess.Popen([reaper_path], env=env)
        
        # Wait a bit for REAPER to start
        print("REAPER process started. PID:", process.pid)
        return True
        
    except Exception as e:
        print(f"Error launching REAPER: {e}")
        return False


def initialize_reapy():
    """
    Performs a full Reapy initialization procedure:
    
    1. Starts REAPER with the correct PYTHONHOME
    2. Waits for REAPER to fully load (5 seconds)
    3. Executes basic Reapy configuration twice to ensure initialization
    4. Restarts REAPER to ensure changes take effect
    5. Creates a new project with a test track
    
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    try:
        # Step 1: Launch REAPER with correct PYTHONHOME
        print("Step 1: Launching REAPER with correct PYTHONHOME...")
        if not launch_reaper_with_pythonhome():
            print("Failed to launch REAPER")
            return False
        
        # Step 2: Wait for REAPER to fully load
        print("Step 2: Waiting for REAPER to initialize (5 seconds)...")
        time.sleep(5)
        
        # Step 3: Execute Reapy configuration twice
        print("Step 3: Configuring Reapy (first attempt)...")
        try:
            import reapy
            # reapy.configure_reaper()
            # print("First Reapy configuration successful")
            #
            # print("Configuring Reapy (second attempt)...")
            # reapy.configure_reaper()
            # print("Second Reapy configuration successful")
        except Exception as e:
            print(f"Error during Reapy configuration: {e}")
            return False
        
        # Step 4: Close and restart REAPER
        print("Step 4: Closing REAPER...")
        try:
            reapy.Project.close_all_projects()
            time.sleep(1)  # Give REAPER time to close projects
            current_project = reapy.Project()
            current_project.close()
        except Exception as e:
            print(f"Warning: Error closing projects: {e}")
        
        print("Restarting REAPER...")
        if not launch_reaper_with_pythonhome():
            print("Failed to restart REAPER")
            return False
        
        time.sleep(5)  # Wait for REAPER to restart
        
        # Step 5: Test Reapy functionality by creating a project and adding a track
        print("Step 5: Testing Reapy by creating a new project with a track...")
        try:
            import reapy
            
            # Create a new project
            reapy.perform_action(40023)  # New project action
            time.sleep(1)  # Give REAPER time to create the project
            
            # Get the current project
            project = reapy.Project()
            
            # Add a new track
            track = project.add_track(index=0, name="Test Track")
            print(f"Successfully created track: {track.name}")
            
            # Test basic Reapy commands
            print(f"Project sample rate: {project.sample_rate}")
            print(f"Number of tracks: {len(project.tracks)}")
            
            # # Import from renardo_reapy
            # try:
            #     import renardo_reapy.runtime as runtime
            #     import renardo_reapy.reascript_api as RPR
            #     RPR.ShowConsoleMsg("Renardo Reapy integration initialized successfully!")
            #     print("Renardo Reapy import successful")
            # except Exception as e:
            #     print(f"Warning: Error importing renardo_reapy: {e}")
            
            return True
            
        except Exception as e:
            print(f"Error testing Reapy functionality: {e}")
            return False
    
    except Exception as e:
        print(f"Error during Reapy initialization process: {e}")
        return False


# Test code
if __name__ == "__main__":
    # print("Starting Reapy initialization test...")
    # success = initialize_reapy()
    #
    # time.sleep(130)
    # print(f"Reapy initialization {'successful' if success else 'failed'}")

    launch_reaper_with_pythonhome()

    
    """
    # Additional testing code if needed
    
    from renardo.runtime import *
    
    from renardo.reaper_backend.ReaperIntegration import init_reapy_project, ReaperInstrumentFactory
    
    old_style_presets = {}
    
    reaproject = init_reapy_project()
    
    reainstru_factory = ReaperInstrumentFactory(old_style_presets, reaproject)
    
    add_chains = reainstru_factory.add_chains
    instanciate = reainstru_factory.instanciate
    
    gone = instanciate("chan1", "pads/gone_1")
    # gonec = instanciate("chan1", "effects/limit2_0")
    # bass303 = instanciate("chan2", "bass/bass303_2")
    # bass303c = instanciate("chan2", "effects/limit2_0")
    
    g1 = Player()
    g1 >> gone(0)
    """