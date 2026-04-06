import os
import subprocess
from sys import platform
import pathlib
import psutil
from ...process_manager import ProcessManager, ProcessType, get_process_manager
from ...logger import get_main_logger


class SupercolliderInstance:

    def __init__(self):
        # Legacy attributes for backward compatibility
        self.sclang_process = None
        self.supercollider_ready = None
        self.sc_app_path = None
        
        # New process manager integration
        self.process_manager = get_process_manager()
        self.logger = get_main_logger()
        self.sclang_process_id = None

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
            # Standard macOS application paths
            standard_paths = [
                "/Applications/SuperCollider.app",
                os.path.expanduser("~/Applications/SuperCollider.app")
            ]
            
            # Try to find SuperCollider app and use absolute path to sclang
            sclang_found = False
            for path in standard_paths:
                if os.path.exists(path):
                    self.sc_app_path = path
                    sclang_path = os.path.join(path, "Contents/MacOS/sclang")
                    if os.path.exists(sclang_path):
                        self.sclang_exec = [sclang_path, '-i', 'scqt']
                        self.check_exec = [sclang_path, '-version']
                        sclang_found = True
                        break
            
            # Fallback to system sclang if not found in standard paths
            if not sclang_found:
                self.sclang_exec = ["sclang", '-i', 'scqt']
                self.check_exec = ["sclang", '-version']
        
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
        # Check if we already have a managed process running
        if self.sclang_process_id and self.process_manager.get_process_status(self.sclang_process_id):
            from ...process_manager.base import ProcessStatus
            status = self.process_manager.get_process_status(self.sclang_process_id)
            if status == ProcessStatus.RUNNING:
                return True
        
        # Check for existing sclang processes
        for process in psutil.process_iter():
            try:
                if 'sclang' in process.name():
                    self.logger.warning(f"Found existing sclang process (PID: {process.pid})")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Prepare configuration for process manager
        config = {
            'capture_output': True,
            'init_code': 'Renardo.start; Renardo.midi;'
        }

        # Add sclang path if we have it from legacy detection
        if hasattr(self, 'sclang_exec') and self.sclang_exec:
            config['sclang_path'] = self.sclang_exec[0]
        
        # Start sclang process via process manager
        try:
            self.sclang_process_id = self.process_manager.start_process(
                ProcessType.SCLANG, 
                config
            )
            
            if self.sclang_process_id:
                # Update legacy attribute for backward compatibility
                process_info = self.process_manager.get_process_info(self.sclang_process_id)
                if process_info and 'pid' in process_info:
                    # Create a mock process object for backward compatibility
                    class MockProcess:
                        def __init__(self, pid, process_manager, sclang_process_id):
                            self.pid = pid
                            self.stdin = None
                            self.stdout = None
                            self.stderr = None
                            self._process_manager = process_manager
                            self._sclang_process_id = sclang_process_id

                        def poll(self):
                            from ...process_manager.base import ProcessStatus
                            status = self._process_manager.get_process_status(self._sclang_process_id)
                            return None if status == ProcessStatus.RUNNING else 0

                    self.sclang_process = MockProcess(process_info['pid'], self.process_manager, self.sclang_process_id)
                
                self.logger.info("sclang process started successfully via process manager")
                return True
            else:
                self.logger.error("Failed to start sclang process")
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting sclang: {e}")
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
        # Use process manager if available
        if self.sclang_process_id:
            success = self.process_manager.execute_code(self.sclang_process_id, code_string)
            if not success:
                raise RuntimeError("Failed to execute code via process manager")
            return
        
        # Fallback to legacy method
        if self.sclang_process is None or self.sclang_process.stdin is None:
            raise RuntimeError("SuperCollider process is not running or stdin is not available")
            
        raw = code_string.encode("utf-8") + b"\x1b"
        self.sclang_process.stdin.write(raw)
        self.sclang_process.stdin.flush()

        # TODO : find a way to consistently stop sclang and scsynth when renardo stops/dies
        # TODO : find a way to name/tag the sclang/synth processes with name renardo to find it better
        # TODO : Use name renardo for scsynth audio server (for example with JACK Driver)

    def is_sclang_running(self):
        # Check via process manager first
        if self.sclang_process_id:
            from ...process_manager.base import ProcessStatus
            status = self.process_manager.get_process_status(self.sclang_process_id)
            if status == ProcessStatus.RUNNING:
                return True
        
        # Legacy check if our stored process is running
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

    def list_audio_devices(self):
        """Get available audio devices by querying SuperCollider.

        Uses the running SclangProcess (via process manager) if available.
        Otherwise starts a temporary SclangProcess just for this query.

        Returns:
            dict: {'output': {index: name}, 'input': {index: name}}, or None on failure
        """
        from ...process_manager.sclang_process import SclangProcess
        from ...process_manager.base import ProcessStatus

        # --- Path 1: reuse the already-running sclang instance ---
        if self.sclang_process_id:
            status = self.process_manager.get_process_status(self.sclang_process_id)
            if status == ProcessStatus.RUNNING:
                sc_process = self.process_manager.get_process(self.sclang_process_id)
                if sc_process is not None:
                    return sc_process.list_audio_devices()

        # --- Path 2: start a temporary SclangProcess for the query ---
        if not self.is_supercollider_ready():
            return None

        import uuid
        temp_id = f"sclang_audio_query_{uuid.uuid4().hex[:8]}"
        config = {'capture_output': True}
        if hasattr(self, 'sclang_exec') and self.sclang_exec:
            config['sclang_path'] = self.sclang_exec[0]

        temp_process = SclangProcess(temp_id, config)
        try:
            if not temp_process.start():
                return None
            return temp_process.list_audio_devices()
        finally:
            temp_process.stop()
