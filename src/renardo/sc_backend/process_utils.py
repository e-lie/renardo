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

    if platform == "linux" or platform == "darwin":
        try:
            log("Executing pkill commands for SuperCollider processes", "INFO")
            subprocess.run(["pkill", "scsynth"], check=False)
            subprocess.run(["pkill", "sclang"], check=False)
            import time
            time.sleep(0.5)
            subprocess.run(["pkill", "-9", "scsynth"], check=False)
            subprocess.run(["pkill", "-9", "sclang"], check=False)
            log("SuperCollider processes killed via pkill command", "INFO")
        except Exception as e:
            log(f"Error with pkill command: {e}", "ERROR")

    elif platform == "win32":
        try:
            log("Executing taskkill commands for SuperCollider processes", "INFO")
            subprocess.run(["taskkill", "/F", "/IM", "scsynth.exe"], check=False)
            subprocess.run(["taskkill", "/F", "/IM", "sclang.exe"], check=False)
            log("SuperCollider processes killed via taskkill command", "INFO")
        except Exception as e:
            log(f"Error with taskkill command: {e}", "ERROR")

    log("Using psutil for additional process termination", "INFO")

    sc_processes = []
    for proc in psutil.process_iter():
        try:
            if 'sclang' in proc.name() or 'scsynth' in proc.name():
                sc_processes.append(proc)
                log(f"Terminating SuperCollider process: {proc.name()} (PID: {proc.pid})", "INFO")
                proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            log(f"Error accessing process: {e}", "ERROR")

    if sc_processes:
        import time
        time.sleep(1)
        still_alive = []
        for proc in sc_processes:
            try:
                if proc.is_running():
                    still_alive.append(proc)
            except psutil.NoSuchProcess:
                pass

        for proc in still_alive:
            try:
                log(f"Force killing SuperCollider process: {proc.name()} (PID: {proc.pid})", "WARN")
                proc.kill()
            except Exception as e:
                log(f"Error killing process: {e}", "ERROR")

        time.sleep(0.5)

    sc_still_running = []
    for proc in psutil.process_iter():
        try:
            pname = proc.name()
            if 'sclang' in pname or 'scsynth' in pname:
                sc_still_running.append(proc)
                log(f"Warning: SuperCollider process still running: {pname} (PID: {proc.pid})", "WARN")
        except Exception:
            pass

    if sc_still_running and (platform == "linux" or platform == "darwin"):
        log("Using direct kill command for persistent processes", "WARN")
        for proc in sc_still_running:
            try:
                subprocess.run(["kill", "-9", str(proc.pid)], check=False)
                log(f"Sent SIGKILL to PID {proc.pid}", "INFO")
            except Exception as e:
                log(f"Error with kill command: {e}", "ERROR")

        import time
        time.sleep(0.5)

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
            except Exception:
                pass
        log("Some SuperCollider processes could not be terminated", "WARN")
        return False
    else:
        log("All SuperCollider processes successfully terminated", "SUCCESS")
        return True
