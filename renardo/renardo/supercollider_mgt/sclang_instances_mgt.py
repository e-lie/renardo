import os
import subprocess
from sys import platform
import pathlib
import psutil


class SupercolliderInstance:

    def __init__(self):
        self.sclang_process = None
        self.supercollider_ready = None

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
        else:
            #self.sclang_exec = ["sclang",  str(SC_USER_CONFIG_DIR / 'start_renardo.scd')]
            self.sclang_exec = ["sclang", '-i', 'scqt']
            self.check_exec = ["sclang", '-version']

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
        if not self.is_sclang_running():
            #print("Auto Launching Renardo SC module with SynthDefManagement...")
            self.sclang_process = subprocess.Popen(
                args=self.sclang_exec,
                #shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
            return True
        else:
            return False

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
