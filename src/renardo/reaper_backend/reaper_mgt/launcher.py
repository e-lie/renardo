"""
REAPER launching and configuration utilities for Renardo.

This module provides functions for launching REAPER with the correct environment,
initializing Reapy integration, and managing REAPER configuration.
Cross-platform support for macOS, Windows, and Linux.
"""
import os
import subprocess
import sys
import os.path
import time
import datetime
import shutil
import platform
from pathlib import Path

from .shared_library import get_python_shared_library, is_windows, is_apple


def launch_reaper_with_pythonhome():
    """
    Launch REAPER with the correct PYTHONHOME environment variable.
    
    Cross-platform implementation supporting:
    - macOS: Launches from /Applications/REAPER.app
    - Windows: Launches from standard Program Files location or registry path
    - Linux: Launches from standard locations or PATH
    
    This function:
    1. Uses get_python_shared_library to find the current Python library path
    2. Extracts the Python home directory from the library path
    3. Sets PYTHONHOME environment variable to point to the current Python installation
    4. Detects platform and launches REAPER from the appropriate location
    5. Detaches the REAPER process from the Python script
    
    Returns:
        tuple: (bool, str) - Success status and PYTHONHOME path used
    """
    try:
        # Get the Python shared library path
        python_lib_path = get_python_shared_library()
        print(f"Python shared library found at: {python_lib_path}")
        
        # Extract the Python home directory from the library path
        if is_windows():
            if "\\lib\\python" in python_lib_path or "\\DLLs\\" in python_lib_path:
                # Windows paths may have python under lib or DLLs
                python_home = python_lib_path.split("\\lib\\python")[0] if "\\lib\\python" in python_lib_path else python_lib_path.split("\\DLLs\\")[0]
            else:
                # Fallback to a reasonable guess if the expected pattern isn't found
                python_home = str(Path(sys.executable).parent)
        elif is_apple() or "lib/libpython" in python_lib_path:
            # macOS or Linux with standard lib pattern
            python_home = python_lib_path.split("lib/libpython")[0]
        else:
            # Generic fallback for other platforms
            python_home = str(Path(sys.executable).parent.parent)
        
        print(f"Setting PYTHONHOME to: {python_home}")
        
        # Prepare environment with PYTHONHOME set
        env = os.environ.copy()
        env["PYTHONHOME"] = python_home
        
        # Find REAPER path based on platform
        reaper_path = None
        
        if is_windows():
            # Try standard Program Files locations for 64-bit and 32-bit Windows
            program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
            program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
            
            possible_paths = [
                os.path.join(program_files, "REAPER (x64)", "reaper.exe"),
                os.path.join(program_files, "REAPER", "reaper.exe"),
                os.path.join(program_files_x86, "REAPER", "reaper.exe")
            ]
            
            # Try to import winreg to detect REAPER path from registry
            try:
                import winreg
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\REAPER") as key:
                        reaper_path = winreg.QueryValueEx(key, "InstallPath")[0]
                        if reaper_path:
                            possible_paths.insert(0, os.path.join(reaper_path, "reaper.exe"))
                except FileNotFoundError:
                    # Try 64-bit specific registry key
                    try:
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\REAPER") as key:
                            reaper_path = winreg.QueryValueEx(key, "InstallPath")[0]
                            if reaper_path:
                                possible_paths.insert(0, os.path.join(reaper_path, "reaper.exe"))
                    except FileNotFoundError:
                        pass
            except ImportError:
                print("winreg module not available, skipping registry check")
            
            # Find first existing path
            for path in possible_paths:
                if os.path.exists(path):
                    reaper_path = path
                    break
                    
        elif is_apple():
            # macOS path
            reaper_path = "/Applications/REAPER.app/Contents/MacOS/REAPER"
            
            # Check for alternate locations if the standard one doesn't exist
            if not os.path.exists(reaper_path):
                alt_paths = [
                    os.path.expanduser("~/Applications/REAPER.app/Contents/MacOS/REAPER"),
                    "/Applications/REAPER64.app/Contents/MacOS/REAPER",
                    os.path.expanduser("~/Applications/REAPER64.app/Contents/MacOS/REAPER")
                ]
                for path in alt_paths:
                    if os.path.exists(path):
                        reaper_path = path
                        break
        else:
            # Linux - try standard locations and PATH
            possible_paths = [
                "/usr/local/bin/reaper",
                "/usr/bin/reaper",
                os.path.expanduser("~/bin/reaper"),
                "/opt/REAPER/reaper"
            ]
            
            # Find first existing path
            for path in possible_paths:
                if os.path.exists(path):
                    reaper_path = path
                    break
                    
            # If not found in standard locations, try to find in PATH
            if not reaper_path:
                try:
                    reaper_path = shutil.which("reaper")
                except Exception:
                    pass
        
        if not reaper_path or not os.path.exists(reaper_path):
            print("Error: REAPER application not found. Checked locations:")
            if is_windows():
                for path in possible_paths:
                    print(f"  - {path}")
            elif is_apple():
                print(f"  - /Applications/REAPER.app")
                print(f"  - ~/Applications/REAPER.app")
            else:
                for path in possible_paths:
                    print(f"  - {path}")
                print("  - PATH environment variable")
            return False
        
        # Launch REAPER with the modified environment in a detached process
        print(f"Launching REAPER from: {reaper_path} (detached)")
        
        # Platform-specific launch methods
        if is_windows():
            # Windows-specific launch
            startupinfo = None
            try:
                # Use subprocess with Windows-specific options
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 1  # SW_SHOWNORMAL
                
                process = subprocess.Popen(
                    [reaper_path], 
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
                )
            except Exception as e:
                print(f"Error with Windows-specific launch: {e}, falling back to basic launch")
                process = subprocess.Popen(
                    [reaper_path], 
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL
                )
                
        else:
            # Linux or MacOS launch
            process = subprocess.Popen(
                [reaper_path], 
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True  # Create a new session
            )
        
        print("REAPER process started. PID:", process.pid)
        return True, python_home
        
    except Exception as e:
        print(f"Error launching REAPER: {e}")
        return False, None


def initialize_reapy():
    """
    Performs a simplified Reapy initialization procedure with user confirmations:
    
    1. Starts REAPER with the correct PYTHONHOME
    2. Waits for user confirmation when REAPER is fully loaded
    3. Executes basic Reapy configuration
    4. Restarts REAPER to ensure changes take effect
    
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    try:
        # Step 1: Launch REAPER with correct PYTHONHOME
        print("\n===== Step 1: Launching REAPER with correct PYTHONHOME =====")
        success, pythonhome = launch_reaper_with_pythonhome()
        if not success:
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
                print("Configuring Reapy...")
                reapy.configure_reaper()
                print("Reapy configuration successful")
        except Exception as e:
            print(f"Error during Reapy configuration: {e}")
            return False
        
        # Step 4: Close and restart REAPER
        print("\n===== Step 3: Restarting REAPER =====")
        print("Please close REAPER manually.")
        input("Press Enter once REAPER is closed...")
            
        print("Restarting REAPER...")
        success, pythonhome = launch_reaper_with_pythonhome()
        if not success:
            print("Failed to restart REAPER")
            return False
        
        input("REAPER has been restarted. Please wait until REAPER is fully loaded, then press Enter to continue...")
        
        print("\n===== Reapy initialization completed =====")
        print("You can now use Reapy to control REAPER.")
        return True
    
    except Exception as e:
        print(f"Error during Reapy initialization process: {e}")
        return False


def reinit_reaper_with_backup():
    """
    Reinitialize REAPER by backing up the current user configuration directory.
    
    Cross-platform implementation supporting:
    - macOS: ~/Library/Application Support/REAPER
    - Windows: %APPDATA%\REAPER
    - Linux: ~/.config/REAPER
    
    This function:
    1. Locates the platform-specific REAPER user configuration directory
    2. Creates a backup with a timestamp suffix
    3. The original config will be recreated by REAPER when it's next launched
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Detect the platform-specific REAPER config directory
        home_dir = Path.home()
        reaper_config_dir = None
        
        if is_windows():
            # Windows: Use %APPDATA% environment variable if available, or default to user's AppData/Roaming
            appdata = os.environ.get("APPDATA")
            if appdata:
                reaper_config_dir = Path(appdata) / "REAPER"
            else:
                reaper_config_dir = home_dir / "AppData/Roaming/REAPER"
                
        elif is_apple():
            # macOS: ~/Library/Application Support/REAPER
            reaper_config_dir = home_dir / "Library/Application Support/REAPER"
            
        else:
            # Linux: ~/.config/REAPER (XDG_CONFIG_HOME)
            xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
            if xdg_config_home:
                reaper_config_dir = Path(xdg_config_home) / "REAPER"
            else:
                reaper_config_dir = home_dir / ".config/REAPER"
        
        # Check if the directory exists
        if not reaper_config_dir.exists():
            # Try alternative common locations based on platform
            alternative_paths = []
            
            if is_windows():
                alternative_paths = [
                    home_dir / "AppData/Local/REAPER",
                    # Some installations might put the config in the program directory
                    Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "REAPER/userdata"
                ]
                
            elif is_apple():
                alternative_paths = [
                    home_dir / "Library/Preferences/REAPER",
                    # Some older or custom installations might use this directory
                    home_dir / ".reaper" 
                ]
                
            else:  # Linux
                alternative_paths = [
                    home_dir / ".reaper",
                    home_dir / ".local/share/REAPER",
                    Path("/usr/local/share/REAPER"),
                    Path("/usr/share/REAPER")
                ]
                
            # Check alternatives
            for alt_path in alternative_paths:
                if alt_path.exists():
                    reaper_config_dir = alt_path
                    break
                    
            # If still not found, report error
            if not reaper_config_dir.exists():
                print(f"REAPER config directory not found at {reaper_config_dir} or any alternative locations")
                return False
        
        # Create a timestamp for the backup
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = reaper_config_dir.parent / f"REAPER.backup_{timestamp}"
        
        print(f"Creating backup of REAPER configuration...")
        print(f"Source: {reaper_config_dir}")
        print(f"Destination: {backup_dir}")
        
        # Check if any REAPER instances are running
        if is_windows():
            try:
                # Windows-specific process check using tasklist
                result = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq reaper.exe", "/NH"], 
                    capture_output=True, 
                    text=True, 
                    check=False
                )
                
                if "reaper.exe" in result.stdout.lower():
                    print("WARNING: REAPER is currently running. Please close it before proceeding.")
                    print("Running processes found in tasklist output")
                    return False
                    
            except Exception as e:
                print(f"Warning: Could not check if REAPER is running using tasklist: {e}")
                print("Please make sure REAPER is not running before continuing.")
                
        elif is_apple():
            try:
                # macOS-specific process check using pgrep
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
                print(f"Warning: Could not check if REAPER is running using pgrep: {e}")
                print("Please make sure REAPER is not running before continuing.")
                
        else:
            try:
                # Linux-specific process check using pgrep with a more specific pattern
                # Use -x to require an exact match of the executable name to exclude oom_reaper
                result = subprocess.run(
                    ["pgrep", "-x", "reaper"], 
                    capture_output=True, 
                    text=True, 
                    check=False
                )
                
                # Only proceed if we didn't find an exact match for 'reaper'
                if result.stdout.strip():
                    print("WARNING: REAPER is currently running. Please close it before proceeding.")
                    print("Running processes:", result.stdout.strip())
                    return False
                
                # Additional check for REAPER executable with potential path
                # Use ps and grep with a pattern that only matches 'reaper' at the end of a path
                ps_result = subprocess.run(
                    ["ps", "aux"], 
                    capture_output=True, 
                    text=True, 
                    check=False
                )
                
                # Check if there are any lines containing "reaper" as the last part of a path
                # but exclude lines containing "oom_reaper"
                reaper_processes = []
                for line in ps_result.stdout.splitlines():
                    if "/reaper" in line and "oom_reaper" not in line:
                        reaper_processes.append(line)
                
                if reaper_processes:
                    print("WARNING: REAPER is currently running. Please close it before proceeding.")
                    print("Running processes found in ps output:")
                    for proc in reaper_processes:
                        print(proc)
                    return False
                    
            except Exception as e:
                print(f"Warning: Could not check if REAPER is running using pgrep: {e}")
                print("Please make sure REAPER is not running before continuing.")
        
        # Perform the backup by renaming the directory
        shutil.move(str(reaper_config_dir), str(backup_dir))
        print(f"Backup created successfully")
        
        print("REAPER configuration will be reset on next launch.")
        return True
    
    except Exception as e:
        print(f"Error backing up REAPER configuration: {e}")
        return False


def test_reaper_integration():
    import reapy
    project = reapy.Project()
    # Create a new track for audio
    audio_track = project.add_track(index=-1, name="Test Track")
    if audio_track:
        result = {
            "success": True,
            "message": audio_track.name
        }
    else:
        result = {
            "success": False,
            "message": ""
        }
    return result
        
        