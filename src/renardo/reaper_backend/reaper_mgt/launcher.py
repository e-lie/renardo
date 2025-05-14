"""
REAPER launching and configuration utilities for Renardo.

This module provides functions for launching REAPER with the correct environment,
initializing Reapy integration, and managing REAPER configuration.
"""
import os
import subprocess
import sys
import os.path
import time
import datetime
import shutil
from pathlib import Path

from .shared_library import get_python_shared_library


def launch_reaper_with_pythonhome():
    """
    Launch REAPER.app on macOS with the correct PYTHONHOME environment variable.
    
    This function:
    1. Uses get_python_shared_library to find the current Python library path
    2. Extracts the Python home directory from the library path
    3. Sets PYTHONHOME environment variable to point to the current Python installation
    4. Launches the REAPER application from /Applications/REAPER.app
    5. Detaches the REAPER process from the Python script
    
    Returns:
        bool: True if REAPER was launched successfully, False otherwise
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
        
        # Launch REAPER with the modified environment in a detached process
        print(f"Launching REAPER from: {reaper_path} (detached)")
        
        # Method 1: Use subprocess.DEVNULL to detach standard file descriptors
        process = subprocess.Popen(
            [reaper_path], 
            env=env, 
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True  # Create a new session
        )
        
        # Alternative macOS-specific approach using open command:
        # subprocess.Popen([
        #     "open", "-a", "REAPER", "--env", f"PYTHONHOME={python_home}"
        # ])
        
        print("REAPER process started. PID:", process.pid)
        return True
        
    except Exception as e:
        print(f"Error launching REAPER: {e}")
        return False


def initialize_reapy():
    """
    Performs a full Reapy initialization procedure with user confirmations:
    
    1. Starts REAPER with the correct PYTHONHOME
    2. Waits for user confirmation when REAPER is fully loaded
    3. Executes basic Reapy configuration twice to ensure initialization
    4. Restarts REAPER to ensure changes take effect
    5. Creates a new project with a test track
    
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    try:
        # Step 1: Launch REAPER with correct PYTHONHOME
        print("\n===== Step 1: Launching REAPER with correct PYTHONHOME =====")
        if not launch_reaper_with_pythonhome():
            print("Failed to launch REAPER")
            return False
        
        # Step 2: Wait for user confirmation that REAPER is loaded
        input("\nREAPER has been launched. Please wait until REAPER is fully loaded, then press Enter to continue...")
        
        # Step 3: Execute Reapy configuration
        print("\n===== Step 2: Configuring Reapy =====")
        try:
            import reapy
            
            response = input("Would you like to run reapy.configure_reaper()? (y/n): ")
            if response.lower() in ['y', 'yes']:
                print("Configuring Reapy (first attempt)...")
                reapy.configure_reaper()
                print("First Reapy configuration successful")
                
                response = input("Would you like to run reapy.configure_reaper() a second time? (y/n): ")
                if response.lower() in ['y', 'yes']:
                    print("Configuring Reapy (second attempt)...")
                    reapy.configure_reaper()
                    print("Second Reapy configuration successful")
        except Exception as e:
            print(f"Error during Reapy configuration: {e}")
            return False
        
        # Step 4: Close and restart REAPER
        print("\n===== Step 3: Restarting REAPER =====")
        response = input("Would you like to close and restart REAPER? (y/n): ")
        if response.lower() in ['y', 'yes']:
            print("Closing REAPER...")
            try:
                reapy.Project.close_all_projects()
                current_project = reapy.Project()
                current_project.close()
            except Exception as e:
                print(f"Warning: Error closing projects: {e}")
                print("Please close REAPER manually.")
                input("Press Enter once REAPER is closed...")
            
            print("Restarting REAPER...")
            if not launch_reaper_with_pythonhome():
                print("Failed to restart REAPER")
                return False
            
            input("REAPER has been restarted. Please wait until REAPER is fully loaded, then press Enter to continue...")
        
        # Step 5: Test Reapy functionality
        print("\n===== Step 4: Testing Reapy functionality =====")
        response = input("Would you like to test Reapy by creating a new project and track? (y/n): ")
        if response.lower() in ['y', 'yes']:
            try:
                import reapy
                
                # Create a new project
                print("Creating a new project...")
                reapy.perform_action(40023)  # New project action
                input("Press Enter once the new project is open...")
                
                # Get the current project
                project = reapy.Project()
                
                # Add a new track
                print("Adding a test track...")
                track = project.add_track(index=0, name="Test Track")
                print(f"Successfully created track: {track.name}")
                
                # Test basic Reapy commands
                print(f"Project sample rate: {project.sample_rate}")
                print(f"Number of tracks: {len(project.tracks)}")
                
                # Import from renardo_reapy
                response = input("Would you like to test renardo_reapy import? (y/n): ")
                if response.lower() in ['y', 'yes']:
                    try:
                        import renardo_reapy.runtime as runtime
                        import renardo_reapy.reascript_api as RPR
                        RPR.ShowConsoleMsg("Renardo Reapy integration initialized successfully!")
                        print("Renardo Reapy import successful")
                    except Exception as e:
                        print(f"Warning: Error importing renardo_reapy: {e}")
            
            except Exception as e:
                print(f"Error testing Reapy functionality: {e}")
                return False
        
        print("\n===== Reapy initialization completed =====")
        print("You can now use Reapy to control REAPER.")
        return True
    
    except Exception as e:
        print(f"Error during Reapy initialization process: {e}")
        return False


def reinit_reaper_with_backup():
    """
    Reinitialize REAPER by backing up the current user configuration directory.
    
    This function:
    1. Locates the REAPER user configuration directory in ~/Library/Application Support/REAPER
    2. Creates a backup with a timestamp suffix
    3. The original config will be recreated by REAPER when it's next launched
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Path to REAPER user config directory on macOS
        home_dir = Path.home()
        reaper_config_dir = home_dir / "Library/Application Support/REAPER"
        
        # Check if the directory exists
        if not reaper_config_dir.exists():
            print(f"REAPER config directory not found at {reaper_config_dir}")
            return False
        
        # Create a timestamp for the backup
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = reaper_config_dir.parent / f"REAPER.backup_{timestamp}"
        
        print(f"Creating backup of REAPER configuration...")
        print(f"Source: {reaper_config_dir}")
        print(f"Destination: {backup_dir}")
        
        # Check if any REAPER instances are running
        try:
            result = subprocess.run(
                ["pgrep", "REAPER"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            if result.stdout.strip():
                print("WARNING: REAPER is currently running. Please close it before proceeding.")
                print("Running processes:", result.stdout.strip())
                return False
        except Exception as e:
            print(f"Warning: Could not check if REAPER is running: {e}")
        
        # Perform the backup by renaming the directory
        shutil.move(str(reaper_config_dir), str(backup_dir))
        print(f"Backup created successfully")
        
        print("REAPER configuration will be reset on next launch.")
        return True
    
    except Exception as e:
        print(f"Error backing up REAPER configuration: {e}")
        return False