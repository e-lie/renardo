import os
import subprocess
from sys import platform
import pathlib
import psutil


class SupercolliderInstance:

    def __init__(self):
        self.sclang_process = None
        self.supercollider_ready = None
        self.sc_app_path = None

        if platform == "win32":
            path_glob = list(pathlib.Path("C:\\Program Files").glob("SuperCollider*"))
            if len(path_glob) == 0: # return if no supercollider folder
                self.supercollider_ready = False
            else:
                sc_dir = path_glob[0] # to match SuperCollider-3.version like folders
                os.environ["PATH"] +=  f"{sc_dir};"
                sclang_path = sc_dir / "sclang.exe"
                #self.sclang_exec = [str(sclang_path), str(SC_USER_CONFIG_DIR / 'start_renardo.scd')]
                self.sclang_exec = [str(sclang_path), '-i', 'scqt']
                self.check_exec = [str(sclang_path), '-version']
                
                # Path to the SuperCollider IDE application on Windows
                self.sc_app_path = sc_dir / "scide.exe"
        
        elif platform == "darwin":  # macOS
            # Default sclang command
            self.sclang_exec = ["sclang", '-i', 'scqt']
            self.check_exec = ["sclang", '-version']
            
            # Standard macOS application paths
            standard_paths = [
                "/Applications/SuperCollider.app",
                os.path.expanduser("~/Applications/SuperCollider.app")
            ]
            
            for path in standard_paths:
                if os.path.exists(path):
                    self.sc_app_path = path
                    break
        
        else:  # Linux
            self.sclang_exec = ["sclang", '-i', 'scqt']
            self.check_exec = ["sclang", '-version']
            
            # On Linux, the IDE might be accessible via various commands
            try:
                # Check if scide is in the PATH
                result = subprocess.run(["which", "scide"], capture_output=True, text=True)
                if result.returncode == 0:
                    self.sc_app_path = "scide"
            except:
                # Try generic paths
                standard_paths = [
                    "/usr/bin/scide",
                    "/usr/local/bin/scide"
                ]
                
                for path in standard_paths:
                    if os.path.exists(path):
                        self.sc_app_path = path
                        break

        self.is_supercollider_ready()

    def is_supercollider_ready(self):
        if self.supercollider_ready is None:
            try:
                completed_process = subprocess.run(self.check_exec, capture_output=True)
                self.supercollider_ready = completed_process.returncode==0
            except:
                self.supercollider_ready = False
        return self.supercollider_ready


    def start_sclang_subprocess(self):
        # First check if we already have a process running
        if self.sclang_process is not None:
            try:
                # Check if it's still running
                if self.sclang_process.poll() is None:
                    return True  # Process is already running
                # If we reach here, the process has terminated
            except:
                pass  # Process reference is invalid, create a new one
        
        # At this point, either we don't have a process or it's not running
        # Check if there's any other sclang running that might interfere
        for process in psutil.process_iter():
            try:
                if 'sclang' in process.name():
                    print(f"Warning: Found existing sclang process (PID: {process.pid})")
                    # Don't try to kill it here, just notify
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Start a new sclang process
        try:
            self.sclang_process = subprocess.Popen(
                args=self.sclang_exec,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                bufsize=1,  # Line buffered
                universal_newlines=False  # Use binary mode
            )
            
            # Wait a short time to ensure the process starts properly
            import time
            time.sleep(1)
            
            # Check if the process is actually running
            if self.sclang_process.poll() is not None:
                print(f"Error: sclang process failed to start (exit code: {self.sclang_process.returncode})")
                self.sclang_process = None
                return False
                
            return True
        except Exception as e:
            print(f"Error starting sclang: {e}")
            self.sclang_process = None
            return False

    def read_stdout_line(self):
        """Read a line from the sclang process stdout
        
        Returns:
            str: Line read from stdout, or empty string if process not available
        """
        if self.sclang_process is not None:
            try:
                # Check if process is still running
                if self.sclang_process.poll() is None and self.sclang_process.stdout is not None:
                    return self.sclang_process.stdout.readline().decode("utf-8", errors="replace")
            except Exception as e:
                print(f"Error reading stdout: {e}")
        return ""

    def read_stderr_line(self):
        """Read a line from the sclang process stderr
        
        Returns:
            str: Line read from stderr, or empty string if process not available
        """
        if self.sclang_process is not None:
            try:
                # Check if process is still running
                if self.sclang_process.poll() is None and self.sclang_process.stderr is not None:
                    return self.sclang_process.stderr.readline().decode("utf-8", errors="replace")
            except Exception as e:
                print(f"Error reading stderr: {e}")
        return ""

    def evaluate_sclang_code(self, code_string):
        if self.sclang_process is None or self.sclang_process.stdin is None:
            raise RuntimeError("SuperCollider process is not running or stdin is not available")
            
        raw = code_string.encode("utf-8") + b"\x1b"
        self.sclang_process.stdin.write(raw)
        self.sclang_process.stdin.flush()

        # TODO : find a way to consistently stop sclang and scsynth when renardo stops/dies
        # TODO : find a way to name/tag the sclang/synth processes with name renardo to find it better
        # TODO : Use name renardo for scsynth audio server (for example with JACK Driver)

    def __del__(self):
        pass
        # self.popen.kill() # TODO: fix that the destructor is not called
        # need to clarify the launch and close process of foxdot/renardo !
        # self.popen.wait()

    def is_sclang_running(self):
        # First check if our stored process is running
        if self.sclang_process is not None:
            try:
                # Check if process still exists and is running
                if self.sclang_process.poll() is None:
                    return True
            except:
                pass  # Process likely terminated, continue to fallback check
                
        # Fallback: Check if any sclang process is running
        running = False
        for process in psutil.process_iter():
            try:
                if 'sclang' in process.name():
                    running = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return running
        
    def launch_supercollider_ide(self):
        """Launch the SuperCollider IDE application detached from the parent process
        
        Returns:
            bool: True if the application was launched successfully, False otherwise
        """
        if not self.sc_app_path:
            return False
            
        try:
            if platform == "darwin":  # macOS needs special handling for .app bundles
                # macOS: open command naturally detaches the process
                subprocess.Popen(["open", self.sc_app_path])
            elif platform == "win32":
                # Windows: detach using CREATE_NEW_PROCESS_GROUP and DETACHED_PROCESS flags
                subprocess.Popen(
                    [str(self.sc_app_path)],
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL
                )
            else:
                # Linux: use nohup command to detach scide and avoid closing with renardo process
                import shlex
                if isinstance(self.sc_app_path, str) and os.path.exists(self.sc_app_path):
                    # Direct path
                    cmd = f"nohup {shlex.quote(str(self.sc_app_path))} >/dev/null 2>&1 &"
                    subprocess.Popen(cmd, shell=True)
                else:
                    # Command in PATH
                    cmd = f"nohup {shlex.quote(self.sc_app_path)} >/dev/null 2>&1 &"
                    subprocess.Popen(cmd, shell=True)
            return True
        except Exception as e:
            print(f"Error launching SuperCollider IDE: {e}")
            return False
