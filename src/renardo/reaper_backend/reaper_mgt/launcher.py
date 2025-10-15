"""
REAPER launching and configuration utilities for Renardo.

This module provides functions for launching REAPER with the correct environment
using the unified process manager.
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
from ...process_manager import ProcessType, get_process_manager
from ...logger import get_main_logger


def launch_reaper_with_pythonhome():
    """
    Launch REAPER with the correct PYTHONHOME environment variable using process manager.
    
    Returns:
        tuple: (bool, str) - Success status and process ID
    """
    logger = get_main_logger()
    process_manager = get_process_manager()
    
    try:
        # Get the Python shared library path
        python_lib_path = get_python_shared_library()
        logger.info(f"Python shared library found at: {python_lib_path}")
        
        # Extract Python home directory
        python_home = _extract_python_home(python_lib_path)
        logger.info(f"Setting PYTHONHOME to: {python_home}")
        
        # Prepare configuration for process manager
        config = {
            'pythonhome': python_home,
            'detached': True
        }
        
        # Start Reaper via process manager
        process_id = process_manager.start_process(ProcessType.REAPER, config)
        
        if process_id:
            logger.info(f"REAPER launched successfully with process ID: {process_id}")
            return True, process_id
        else:
            logger.error("Failed to launch REAPER")
            return False, None
            
    except Exception as e:
        logger.error(f"Error launching REAPER: {e}")
        return False, None


def _extract_python_home(python_lib_path):
    """Extract Python home directory from library path."""
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
    
    return python_home


# Legacy reapy functions removed - use process manager instead


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


# Legacy reapy test function removed - use process manager instead
        
        