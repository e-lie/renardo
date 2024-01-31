import os
import subprocess
from sys import platform
import time
import pathlib

import psutil

from renardo.SCFilesHandling import SC_USER_CONFIG_DIR


class SupercolliderInstance:

    def __init__(self):
        self.sclang_process = None

        if platform == "win32":
            sc_dir = next(pathlib.Path("C:\\Program Files").glob("SuperCollider*")) # to match SuperCollider-3.version like folders
            os.environ["PATH"] +=  f"{sc_dir};"
            sclang_path = sc_dir / "sclang.exe"
            #self.sclang_exec = [str(sclang_path), str(SC_USER_CONFIG_DIR / 'start_renardo.scd')]
            self.sclang_exec = [str(sclang_path), '-i', 'scqt']
        else:
            #self.sclang_exec = ["sclang",  str(SC_USER_CONFIG_DIR / 'start_renardo.scd')]
            self.sclang_exec = ["sclang", '-i', 'scqt']


    def start_sclang_subprocess(self):
        if not self.is_sclang_running():
            #print("Auto Launching Renardo SC module with SCLang...")
            self.sclang_process = subprocess.Popen(
                args=self.sclang_exec,
                #shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )

    def read_stdout_line(self):
        if self.sclang_process.returncode is None:
           return self.sclang_process.stdout.readline().decode("utf-8")

    def read_stderr_line(self):
        if self.sclang_process.returncode is None:
            return self.sclang_process.stderr.readline().decode("utf-8")

    def evaluate_sclang_code(self, code_string):
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
        running = False
        for process in psutil.process_iter():
            if 'sclang' in process.name():
                running = True
        return running
