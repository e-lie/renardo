import subprocess
import time

import psutil

from renardo_lib.ServerManager.SCFilesHandling import SC_USER_CONFIG_DIR


class RenardoSupercolliderInstance:
    def __init__(self):
        self.popen = None
        if not self.is_sclang_running():
            self.popen = subprocess.Popen(
                args=['sclang', SC_USER_CONFIG_DIR / 'start_renardo.scd'],
                shell=False,
            )
            time.sleep(1)  # wait a bit for the server to be started
        # TODO : find a way to consistently stop sclang and scsynth when renardo stops/dies
        # TODO : find a way to name/tag the sclang/synth processes with name renardo to find it better
        # TODO : Use name renardo for scsynth audio server (for example with JACK Driver)

    def __del__(self):
        self.popen.kill() # TODO: fix that the destructor is not called
        # need to clarify the launch and close process of foxdot/renardo !
        self.popen.wait()

    def is_sclang_running(self):
        running = False
        for process in psutil.process_iter():
            if 'sclang' in process.name():
                running = True
        return running
