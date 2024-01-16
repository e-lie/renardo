import os
import subprocess
from sys import platform
import time
import pathlib

import psutil

from renardo.SCFilesHandling import SC_USER_CONFIG_DIR


class RenardoSupercolliderInstance:

    def __init__(self):
        self.popen = None

        if platform == "win32":
            sc_dir = next(pathlib.Path("C:\\Program Files").glob("SuperCollider*")) # to match SuperCollider-3.version like folders
            os.environ["PATH"] +=  f"{sc_dir};"
            sclang_path = sc_dir / "sclang.exe"
            sclang_exec = [str(sclang_path), str(SC_USER_CONFIG_DIR / 'start_renardo.scd')]
        else:
            sclang_exec = ["sclang",  SC_USER_CONFIG_DIR / 'start_renardo.scd']

        if not self.is_sclang_running():
            print("Auto Launching Renardo SC module with SCLang...")
            self.popen = subprocess.Popen(
                args=sclang_exec,
                shell=True,
                stdout=subprocess.PIPE,
            )
            time.sleep(1)  # wait a bit for the server to be started
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
