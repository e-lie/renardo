"""REAPER launching and stopping utilities for reaside."""
import os
import subprocess
import sys
import time
import platform
import shutil
from pathlib import Path


def is_windows():
    """Return whether OS is Windows."""
    return os.name == "nt"


def is_apple():
    """Return whether OS is MacOS."""
    return sys.platform == "darwin"


def get_python_shared_library():
    """Return path to Python shared library (.dll, .dylib or .so)."""
    # For this simple implementation, we'll make a reasonable guess based on the Python executable
    if is_windows():
        python_home = str(Path(sys.executable).parent)
        return os.path.join(python_home, "python{0}{1}.dll".format(
            sys.version_info.major, sys.version_info.minor))
    elif is_apple():
        python_home = str(Path(sys.executable).parent.parent)
        return os.path.join(python_home, "lib", "libpython{0}.{1}.dylib".format(
            sys.version_info.major, sys.version_info.minor))
    else:  # Linux
        python_home = str(Path(sys.executable).parent.parent)
        return os.path.join(python_home, "lib", "libpython{0}.{1}.so".format(
            sys.version_info.major, sys.version_info.minor))


def start_reaper(detached=True):
    """Launch REAPER with the correct PYTHONHOME environment variable."""
    try:
        # Get the Python shared library path
        python_lib_path = get_python_shared_library()
        
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
                pass
            
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
            locations = []
            if is_windows():
                locations = possible_paths
            elif is_apple():
                locations = ["/Applications/REAPER.app", "~/Applications/REAPER.app"]
            else:
                locations = possible_paths + ["PATH environment variable"]
            
            return False, None, None
        
        # Launch REAPER with the modified environment
        process = None
        
        # Platform-specific launch methods
        if is_windows():
            # Windows-specific launch
            startupinfo = None
            try:
                # Use subprocess with Windows-specific options
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 1  # SW_SHOWNORMAL
                
                if detached:
                    process = subprocess.Popen(
                        [reaper_path], 
                        env=env,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        stdin=subprocess.DEVNULL,
                        startupinfo=startupinfo,
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
                    )
                else:
                    process = subprocess.Popen(
                        [reaper_path], 
                        env=env,
                        startupinfo=startupinfo
                    )
            except Exception as e:
                # Fall back to basic launch
                if detached:
                    process = subprocess.Popen(
                        [reaper_path], 
                        env=env,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        stdin=subprocess.DEVNULL
                    )
                else:
                    process = subprocess.Popen(
                        [reaper_path], 
                        env=env
                    )
                    
        else:
            # Linux or macOS launch
            if detached:
                process = subprocess.Popen(
                    [reaper_path], 
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True  # Create a new session
                )
            else:
                process = subprocess.Popen(
                    [reaper_path], 
                    env=env,
                    start_new_session=True  # Create a new session
                )
        
        return True, python_home, process
        
    except Exception as e:
        return False, None, None


def stop_reaper():
    """Stop REAPER by finding and terminating REAPER processes."""
    try:
        reaper_processes = []
        
        if is_windows():
            # Windows approach using taskkill
            try:
                # Check if REAPER is running
                check_process = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq reaper.exe", "/NH"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if "reaper.exe" in check_process.stdout.lower():
                    # Kill REAPER process
                    subprocess.run(
                        ["taskkill", "/F", "/IM", "reaper.exe"],
                        capture_output=True,
                        check=False
                    )
                    
                    # Verify REAPER is no longer running
                    time.sleep(1)  # Give some time for the process to terminate
                    verify_process = subprocess.run(
                        ["tasklist", "/FI", "IMAGENAME eq reaper.exe", "/NH"],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    return "reaper.exe" not in verify_process.stdout.lower()
                else:
                    # REAPER was not running
                    return True
                    
            except Exception as e:
                return False
                
        elif is_apple():
            # macOS approach using pkill
            try:
                # Check if REAPER is running
                check_process = subprocess.run(
                    ["pgrep", "REAPER"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if check_process.stdout.strip():
                    # Kill REAPER process
                    subprocess.run(
                        ["pkill", "REAPER"],
                        capture_output=True,
                        check=False
                    )
                    
                    # Verify REAPER is no longer running
                    time.sleep(1)  # Give some time for the process to terminate
                    verify_process = subprocess.run(
                        ["pgrep", "REAPER"],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    return not verify_process.stdout.strip()
                else:
                    # REAPER was not running
                    return True
                    
            except Exception as e:
                return False
                
        else:
            # Linux approach using pkill
            try:
                # Check if REAPER is running (exact match to exclude oom_reaper)
                check_process = subprocess.run(
                    ["pgrep", "-x", "reaper"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                reaper_running = bool(check_process.stdout.strip())
                
                # Additional check for REAPER with full path
                ps_result = subprocess.run(
                    ["ps", "aux"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                for line in ps_result.stdout.splitlines():
                    if "/reaper" in line and "oom_reaper" not in line and "python" not in line and ".py" not in line:
                        reaper_running = True
                        break
                
                if reaper_running:
                    # Kill REAPER processes
                    subprocess.run(
                        ["pkill", "-x", "reaper"],
                        capture_output=True,
                        check=False
                    )
                    
                    # Also try to kill any REAPER with a path
                    for line in ps_result.stdout.splitlines():
                        if "/reaper" in line and "oom_reaper" not in line and "python" not in line and ".py" not in line:
                            parts = line.split()
                            if len(parts) > 1:
                                try:
                                    pid = int(parts[1])
                                    subprocess.run(
                                        ["kill", str(pid)],
                                        capture_output=True,
                                        check=False
                                    )
                                except (ValueError, IndexError):
                                    pass
                    
                    # Verify REAPER is no longer running
                    time.sleep(1)  # Give some time for processes to terminate
                    
                    verify_process = subprocess.run(
                        ["pgrep", "-x", "reaper"],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    verify_ps = subprocess.run(
                        ["ps", "aux"],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    still_running = bool(verify_process.stdout.strip())
                    
                    # Check if there are any remaining REAPER processes
                    for line in verify_ps.stdout.splitlines():
                        if "/reaper" in line and "oom_reaper" not in line and "python" not in line and ".py" not in line:
                            still_running = True
                            break
                    
                    return not still_running
                else:
                    # REAPER was not running
                    return True
                    
            except Exception as e:
                return False
        
        # Should not reach here
        return False
        
    except Exception as e:
        return False


def is_reaper_running():
    """Check if REAPER is currently running."""
    try:
        if is_windows():
            # Windows check using tasklist
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq reaper.exe", "/NH"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            return "reaper.exe" in result.stdout.lower()
                
        elif is_apple():
            # macOS check using pgrep
            result = subprocess.run(
                ["pgrep", "REAPER"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            return bool(result.stdout.strip())
                
        else:
            # Linux check using pgrep and ps
            reaper_running = False
            
            # Use pgrep with exact match to exclude oom_reaper
            result = subprocess.run(
                ["pgrep", "-x", "reaper"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            if result.stdout.strip():
                reaper_running = True
            
            # Additional check using ps to find REAPER with path
            if not reaper_running:
                ps_result = subprocess.run(
                    ["ps", "aux"], 
                    capture_output=True, 
                    text=True, 
                    check=False
                )
                
                for line in ps_result.stdout.splitlines():
                    if "/reaper" in line and "oom_reaper" not in line and "python" not in line and ".py" not in line:
                        reaper_running = True
                        break
            
            return reaper_running
    
    except Exception:
        # If we can't determine, assume it's not running
        return False


def get_reaper_fxchains_dir():
    """Get REAPER's FXChains directory path."""
    from renardo.settings_manager import settings
    from renardo.logger import get_logger
    
    logger = get_logger('reaside.tools.reaper_program')
    
    try:
        # Get REAPER resource path from settings
        reaper_resource_path = settings.get("reaper_backend.REAPER_RESOURCE_PATH")
        
        if reaper_resource_path and Path(reaper_resource_path).exists():
            fxchains_dir = Path(reaper_resource_path) / "FXChains"
            if fxchains_dir.exists():
                return fxchains_dir
        
        # Try common REAPER installation paths
        possible_paths = []
        
        if is_windows():
            possible_paths.extend([
                Path(os.environ.get('APPDATA', '')) / "REAPER" / "FXChains",
                Path("C:/Users") / os.environ.get('USERNAME', '') / "AppData/Roaming/REAPER/FXChains",
            ])
        else:  # macOS/Linux
            home = Path.home()
            possible_paths.extend([
                home / "Library/Application Support/REAPER/FXChains",  # macOS
                home / ".config/REAPER/FXChains",  # Linux
            ])
        
        for path in possible_paths:
            if path.exists():
                return path
        
        logger.error(f"Could not find REAPER FXChains directory. Tried: {possible_paths}")
        return None
        
    except Exception as e:
        logger.error(f"Error determining REAPER FXChains directory: {e}")
        return None

