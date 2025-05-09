"""
Utility functions for controlling SuperCollider processes
"""
import subprocess
import sys
import psutil
from sys import platform

def kill_supercollider_processes(logger=None):
    """
    Kill all SuperCollider processes (sclang and scsynth)
    
    Args:
        logger: Optional logger to record process information
        
    Returns:
        bool: True if all processes were successfully terminated
    """
    def log(message, level="INFO"):
        if logger:
            if hasattr(logger, 'write_line'):
                logger.write_line(message, level)
            else:
                print(f"[{level}] {message}")
        else:
            print(f"[{level}] {message}")
    
    log("Stopping SuperCollider backend processes...", "INFO")
    
    # Track if we need to use psutil as a fallback
    use_psutil_fallback = False
    
    # Use platform-specific commands to kill SC processes
    if platform == "linux" or platform == "darwin":  # Linux or macOS
        # Use pkill command which is more reliable on Unix systems
        try:
            log("Executing pkill commands for SuperCollider processes", "INFO")
            subprocess.run(["pkill", "scsynth"], check=False)
            subprocess.run(["pkill", "sclang"], check=False)
            log("SuperCollider processes killed via pkill command", "INFO")
        except Exception as e:
            log(f"Error with pkill command: {e}", "ERROR")
            
            # Fallback to using psutil
            log("Falling back to psutil for process termination", "WARN")
            use_psutil_fallback = True
    elif platform == "win32":  # Windows
        # On Windows, use taskkill which is more reliable
        try:
            log("Executing taskkill commands for SuperCollider processes", "INFO")
            subprocess.run(["taskkill", "/F", "/IM", "scsynth.exe"], check=False)
            subprocess.run(["taskkill", "/F", "/IM", "sclang.exe"], check=False)
            log("SuperCollider processes killed via taskkill command", "INFO")
        except Exception as e:
            log(f"Error with taskkill command: {e}", "ERROR")
            
            # Fallback to using psutil
            log("Falling back to psutil for process termination", "WARN")
            use_psutil_fallback = True
    else:
        # Unknown platform, use psutil as fallback
        log(f"Using generic process termination for platform: {platform}", "INFO")
        use_psutil_fallback = True
        
    # Fallback method using psutil if needed
    if use_psutil_fallback:
        # Stop all SuperCollider processes
        for proc in psutil.process_iter():
            try:
                if 'sclang' in proc.name() or 'scsynth' in proc.name():
                    log(f"Terminating SuperCollider process: {proc.name()} (PID: {proc.pid})", "INFO")
                    proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                log(f"Error terminating process: {e}", "ERROR")
                pass
        
        # Wait for processes to terminate (with timeout)
        gone, still_alive = psutil.wait_procs([p for p in psutil.process_iter() 
                                             if 'sclang' in p.name() or 'scsynth' in p.name()], 
                                             timeout=3)
        
        # Force kill any remaining processes
        for p in still_alive:
            try:
                log(f"Force killing SuperCollider process: {p.name()} (PID: {p.pid})", "WARN")
                p.kill()
            except Exception as e:
                log(f"Error killing process: {e}", "ERROR")
                pass
    
    # Final verification that processes are stopped
    sc_still_running = False
    for proc in psutil.process_iter():
        try:
            if 'sclang' in proc.name() or 'scsynth' in proc.name():
                sc_still_running = True
                log(f"Warning: SuperCollider process still running: {proc.name()} (PID: {proc.pid})", "WARN")
        except Exception:
            pass
    
    if sc_still_running:
        log("Some SuperCollider processes could not be terminated", "WARN")
        return False
    else:
        log("All SuperCollider processes successfully terminated", "SUCCESS")
        return True