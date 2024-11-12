#!/usr/bin/python

"""

FoxDot is a Python library and programming environment that provides a fast and
user-friendly abstraction to the powerful audio-engine, SuperCollider. It comes
with its own IDE, which means it can be used straight out of the box; all you
need is Python and SuperCollider and you're ready to go!

Copyright Ryan Kirkbride 2015
"""

import sys
from renardo_lib.runtime import *


def boot_supercollider():
    """ Uses subprocesses to boot supercollider from the cli """
    import time
    import platform
    import os
    import subprocess
    import getpass
    try:
        import psutil
    except ImportError:
        os.system("pip install psutil")
        import sys
        sys.exit("Installed psutil, please start FoxDot again.")

    sclangpath = ""  # find path to sclang
    thispath = ""  # find this path
    thisdir = os.getcwd()
    OS = platform.system()
    username = getpass.getuser()

    if (OS == "Windows"):
        sclangloc = os.popen('where /R "C:\\Program Files" sclang.exe').read()
        thiscwd = str(sclangloc)
        ourcwd = thiscwd.replace('\\sclang.exe\n', '')

        def is_proc_running(name):
            for p in psutil.process_iter(attrs=["name", "exe", "cmdline"]):
                # print(p);
                procname = p.info['name'] or \
                     p.info['exe'] and os.path.basename(p.info['exe']) == name\
                     or p.info['cmdline'] and p.info['cmdline'][0] == name
                if (procname.startswith(name)):
                    return True
            return False

        running = (is_proc_running("sclang"))

        if (running is False):
            startup = thisdir+"/FoxDot/startup.scd"
            # os.system("sclang"+startup+" &")
            subprocess.Popen([sclangloc, startup], cwd=ourcwd, shell=True)

    elif (OS == "Linux"):
        def is_proc_running(name):
            for p in psutil.process_iter(attrs=["name", "cmdline"]):
                # print(p);
                procname = p.info['name'] or \
                     p.info['cmdline'] and p.info['cmdline'][0] == name
                if (procname.startswith(name)):
                    return True

        running = (is_proc_running("sclang"))

        if (running is False):
            startup = thisdir+"/FoxDot/startup.scd"
            # os.system('sclang "/home/foxdot/Desktop/FoxDot-Cross-Platform/
            # FoxDot/startup.scd" &') #functional
            os.system("sclang "+startup+" &")

    else:
        print("Operating system unrecognised")
        # Potentially get the user to choose their OS from a list?
        # Then run the corresponding functions#


if "--boot" in sys.argv:
    boot_supercollider()
    sys.argv.remove("--boot")


def main():
    """ Function for starting the GUI when importing the library """
    from FoxDotEditor.Editor import workspace
    FoxDot = workspace(FoxDotCode).run()


def Go():
    """ Function to be called at the end of Python files with FoxDot code in to
    keep the TempoClock thread alive. """
    try:
        import time
        while 1:
            time.sleep(100)
    except KeyboardInterrupt:
        return
