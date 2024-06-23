import os
import subprocess
from sys import platform
import pathlib

import psutil

class PulsarNotFoundError(Exception):
    pass

class PulsarAlreadyRunning(Exception):
    pass

class PulsarInstance:

    def __init__(self):
        self.pulsar_process = None
        self.pulsar_ready = None

        if platform == "win32":
            # if chocolatey pulsar is installed in appdata
            pulsar_appdata_path = pathlib.Path(os.getenv('LOCALAPPDATA')) / 'Programs' / 'Pulsar' / 'Pulsar.exe'
            #
            pulsar_c_path = pathlib.WindowsPath(os.getenv('ProgramFiles')) / 'Pulsar' / 'Pulsar.exe'
            if pulsar_appdata_path.exists():
                self.pulsar_exec = [str(pulsar_appdata_path)]
                self.check_exec = [str(pulsar_appdata_path),'--version']
            elif pulsar_c_path.exists():
                self.pulsar_exec = [str(pulsar_c_path)]
                self.check_exec = [str(pulsar_c_path),'--version']
            else:
                self.pulsar_ready = False
        elif platform == "Darwin":
            pulsar_path = pathlib.Path("/Applications" / "Pulsar.app")
            self.pulsar_exec = ['open', str(pulsar_path)]
            self.check_exec = ['open', str(pulsar_path), "--version"]
        else:
            self.pulsar_exec = ["pulsar"]
            self.check_exec = ["pulsar", "--version"]
        self.is_pulsar_ready()


    def is_pulsar_ready(self):
        if self.pulsar_ready is None:
            try:
                completed_process = subprocess.run(self.check_exec, capture_output=True)
                self.pulsar_ready = completed_process.returncode==0
            except:
                self.pulsar_ready = False
        return self.pulsar_ready


    def start_pulsar_subprocess(self):
        try:
            if self.is_pulsar_running():
                raise PulsarAlreadyRunning()
            self.pulsar_process = subprocess.Popen(
                    args=self.pulsar_exec,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
            )
            return "Pulsar started"
        except Exception as e:
            return f"Pulsar not started: {e}"

    def read_stdout_line(self):
        if self.pulsar_process.returncode is None:
           return self.pulsar_process.stdout.readline().decode("utf-8")

    def read_stderr_line(self):
        if self.pulsar_process.returncode is None:
            return self.pulsar_process.stderr.readline().decode("utf-8")

    def evaluate_sclang_code(self, code_string):
        raw = code_string.encode("utf-8") + b"\x1b"
        self.pulsar_process.stdin.write(raw)
        self.pulsar_process.stdin.flush()

        # TODO : find a way to consistently stop sclang and scsynth when renardo stops/dies
        # TODO : find a way to name/tag the sclang/synth processes with name renardo to find it better
        # TODO : Use name renardo for scsynth audio server (for example with JACK Driver)

    def __del__(self):
        pass
        # self.popen.kill() # TODO: fix that the destructor is not called
        # need to clarify the launch and close process of foxdot/renardo !
        # self.popen.wait()

    def is_pulsar_running(self):
        running = False
        for process in psutil.process_iter():
            if 'pulsar' in process.name().lower():
                running = True
        return running
