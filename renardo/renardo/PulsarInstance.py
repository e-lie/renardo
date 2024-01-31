import os
import subprocess
from sys import platform
import time
import pathlib

import psutil

from renardo.SCFilesHandling import SC_USER_CONFIG_DIR

class PulsarNotFoundError(Exception):
    pass

class PulsarInstance:

    def __init__(self):
        self.pulsar_process = None

        if platform == "win32":
            # if chocolatey
            pulsar_appdata_path = pathlib.Path(os.getenv('LOCALAPPDATA')) / 'Programs' / 'Pulsar' / 'Pulsar.exe'
            pulsar_c_path = pathlib.WindowsPath("C:") / 'Program Files' / 'Pulsar' / 'Pulsar.exe'
            if pulsar_appdata_path.exists():
                self.pulsar_exec = [str(pulsar_appdata_path)]
            elif pulsar_c_path.exists():
                self.pulsar_exec = [str(pulsar_c_path)]
            else:
                raise PulsarNotFoundError
        elif platform == "Darwin":
            pulsar_path = pathlib.Path("/Applications" / "Pulsar.app")
            self.pulsar_exec = ['open', str(pulsar_path)]
        else:
            self.pulsar_exec = ["pulsar"]


    def start_pulsar_subprocess(self):
        if not self.is_pulsar_running():
            self.pulsar_process = subprocess.Popen(
                 args=self.pulsar_exec,
                 #shell=True,
                 stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE,
                 stdin=subprocess.PIPE,
            )

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
