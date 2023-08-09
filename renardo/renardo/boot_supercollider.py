import subprocess
import psutil # need to be added as a dependency


def is_sclang_running():
    running = False
    for process in psutil.process_iter():
        if 'sclang' in process.name():
            running = True
    return running

def boot_supercollider():
    if not is_sclang_running():
        subprocess.Popen(['sclang', '/home/elie/Bureau/Livecoding/tech_setup/start_foxdot.sc'])

