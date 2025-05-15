"""
Utility functions for controlling SuperCollider processes
"""
import subprocess
import sys
import psutil
from sys import platform

def kill_supercollider_processes(logger=None, force=False):
    """
    Kill all SuperCollider processes (sclang and scsynth)
    
    Args:
        logger: Optional logger to record process information
        force: Force kill all processes even if platform-specific commands worked
        
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
    
    # Always use both platform-specific commands AND psutil for maximum reliability
    
    # Use platform-specific commands to kill SC processes
    if platform == "linux" or platform == "darwin":  # Linux or macOS
        # Use pkill command which is more reliable on Unix systems
        try:
            log("Executing pkill commands for SuperCollider processes", "INFO")
            # Try with SIGTERM first
            subprocess.run(["pkill", "scsynth"], check=False)
            subprocess.run(["pkill", "sclang"], check=False)
            
            # Allow a moment for graceful termination
            import time
            time.sleep(0.5)
            
            # Then force kill with SIGKILL if needed
            subprocess.run(["pkill", "-9", "scsynth"], check=False)
            subprocess.run(["pkill", "-9", "sclang"], check=False)
            
            log("SuperCollider processes killed via pkill command", "INFO")
        except Exception as e:
            log(f"Error with pkill command: {e}", "ERROR")
    
    elif platform == "win32":  # Windows
        # On Windows, use taskkill which is more reliable
        try:
            log("Executing taskkill commands for SuperCollider processes", "INFO")
            subprocess.run(["taskkill", "/F", "/IM", "scsynth.exe"], check=False)
            subprocess.run(["taskkill", "/F", "/IM", "sclang.exe"], check=False)
            log("SuperCollider processes killed via taskkill command", "INFO")
        except Exception as e:
            log(f"Error with taskkill command: {e}", "ERROR")
    
    # Always use psutil as well to ensure thoroughness
    log("Using psutil for additional process termination", "INFO")
    
    # First attempt: graceful termination
    sc_processes = []
    for proc in psutil.process_iter():
        try:
            if 'sclang' in proc.name() or 'scsynth' in proc.name():
                sc_processes.append(proc)
                log(f"Terminating SuperCollider process: {proc.name()} (PID: {proc.pid})", "INFO")
                proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            log(f"Error accessing process: {e}", "ERROR")
    
    # Wait for processes to terminate (with timeout)
    if sc_processes:
        import time
        
        # Wait for graceful termination
        time.sleep(1)
        
        # Check which processes are still alive
        still_alive = []
        for proc in sc_processes:
            try:
                if proc.is_running():
                    still_alive.append(proc)
            except psutil.NoSuchProcess:
                pass  # Process already terminated
        
        # Force kill any remaining processes
        for proc in still_alive:
            try:
                log(f"Force killing SuperCollider process: {proc.name()} (PID: {proc.pid})", "WARN")
                proc.kill()
            except Exception as e:
                log(f"Error killing process: {e}", "ERROR")
        
        # Allow a moment for processes to fully exit
        time.sleep(0.5)
    
    # Final verification that processes are stopped
    sc_still_running = []
    for proc in psutil.process_iter():
        try:
            pname = proc.name()
            if 'sclang' in pname or 'scsynth' in pname:
                sc_still_running.append(proc)
                log(f"Warning: SuperCollider process still running: {pname} (PID: {proc.pid})", "WARN")
        except Exception:
            pass
    
    # Last resort: if on Linux, try the 'kill' command directly for persisting processes
    if sc_still_running and (platform == "linux" or platform == "darwin"):
        log("Using direct kill command for persistent processes", "WARN")
        for proc in sc_still_running:
            try:
                subprocess.run(["kill", "-9", str(proc.pid)], check=False)
                log(f"Sent SIGKILL to PID {proc.pid}", "INFO")
            except Exception as e:
                log(f"Error with kill command: {e}", "ERROR")
        
        # Allow a moment for processes to fully exit
        import time
        time.sleep(0.5)
        
        # Final check
        sc_still_running = []
        for proc in psutil.process_iter():
            try:
                if 'sclang' in proc.name() or 'scsynth' in proc.name():
                    sc_still_running.append(proc)
            except Exception:
                pass
    
    if sc_still_running:
        for proc in sc_still_running:
            try:
                log(f"SuperCollider process still running: {proc.name()} (PID: {proc.pid})", "WARN")
            except:
                pass
        log("Some SuperCollider processes could not be terminated", "WARN")
        return False
    else:
        log("All SuperCollider processes successfully terminated", "SUCCESS")
        return True