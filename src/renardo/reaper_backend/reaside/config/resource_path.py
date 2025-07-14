"""Get REAPER resource path."""

import os
import platform
import psutil
import sys
import warnings


def get_resource_path(detect_portable_install=True):
    """Return path to REAPER resource directory.

    Parameters
    ----------
    detect_portable_install : bool, optional
        If ``True``, this function will look for a currently running
        REAPER process and detect whether it is a portable install.
        If ``False``, configuration files will be looked for in the
        default locations only, which may result in a
        ``FileNotFoundError`` if no global REAPER install exists.

    Returns
    -------
    path : str
        Path to REAPER resource directory (contains reaper.ini).

    Raises
    ------
    RuntimeError
        When ``detect_portable_install=True`` and zero or more than one
        REAPER instances are currently running.
    FileNotFoundError
        When ``detect_portable_install=False`` but no global
        configuration file can be found (which means REAPER has only
        been installed as portable.)
    """
    system = platform.system()
    # First look in hard-coded paths
    hardcoded_paths = {
        'Windows': [
            os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'REAPER')
        ],
        'Darwin': [
            os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'REAPER')
        ],
        'Linux': [
            os.path.join(os.path.expanduser('~'), '.config', 'REAPER')
        ]
    }
    
    if system in hardcoded_paths:
        for path in hardcoded_paths[system]:
            # Try both lowercase and mixed case for reaper.ini
            for ini_name in ['reaper.ini', 'REAPER.INI', 'Reaper.ini']:
                ini_path = os.path.join(path, ini_name)
                print(f"Checking for REAPER config at: {ini_path}")
                
                try:
                    if os.path.exists(ini_path):
                        print(f"Found REAPER config at: {ini_path}")
                        return path
                except Exception as e:
                    print(f"Error checking {ini_path}: {str(e)}")
            
            # If we get here, no reaper.ini was found
            print(f"No reaper.ini variants found at: {path}")
            
            # Check if directory exists but no reaper.ini
            if os.path.isdir(path):
                print(f"Directory exists at {path}, but no reaper.ini found")
                try:
                    dir_contents = os.listdir(path)
                    print(f"Directory contents: {dir_contents}")
                    # Check for any .ini files that might be reaper related
                    ini_files = [f for f in dir_contents if f.lower().endswith('.ini')]
                    if ini_files:
                        print(f"INI files found: {ini_files}")
                        # If any reaper-related ini exists, let's try using this directory anyway
                        for f in ini_files:
                            if 'reaper' in f.lower():
                                print(f"Found reaper-related ini file: {f}")
                                return path
                except Exception as e:
                    print(f"Error listing directory {path}: {str(e)}")
    
    # If not found and portable detection is enabled, try to find running REAPER process
    if detect_portable_install:
        reaper_processes = []
        for process in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                # More precise detection to filter out false positives like oom_reaper
                process_name = process.info['name'].lower()
                
                # Common REAPER executable names
                reaper_names = [
                    "reaper", 
                    "reaper.exe", 
                    "reaperlite", 
                    "reaperlite.exe",
                    "reaper64", 
                    "reaper64.exe",
                    "reaper-x86_64",
                    "reaper-arm64",
                    "reaper-gtk",
                    "reaperwl",
                    "reaperdpio",
                    "reaper6",
                    "reaper6.exe"
                ]
                
                # Only match exact REAPER binary names to avoid system processes like "oom_reaper"
                if process_name in reaper_names:
                    reaper_processes.append(process)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if len(reaper_processes) == 0:
            raise RuntimeError(
                "No running REAPER instances found. Please start REAPER and try again."
            )
        if len(reaper_processes) > 1:
            # Provide more details to help debugging
            process_details = ", ".join([f"{p.info['name']} (PID: {p.pid})" for p in reaper_processes])
            raise RuntimeError(
                f"Multiple REAPER instances are running: {process_details}. Please close all but one."
            )
        
        # Found exactly one REAPER process
        reaper_process = reaper_processes[0]
        reaper_exe_path = reaper_process.info['exe']
        
        # Resource path is in the same directory as the executable for portable installations
        resource_path = os.path.dirname(reaper_exe_path)
        if os.path.exists(os.path.join(resource_path, 'reaper.ini')):
            return resource_path
    
    # If we get here, couldn't find resource path
    raise FileNotFoundError(
        "Could not find REAPER resource directory. REAPER might be installed as portable only."
    )