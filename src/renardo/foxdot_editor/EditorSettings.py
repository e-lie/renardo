import os.path
import sys

FOXDOT_EDITOR_ROOT = os.path.realpath(__file__ + "/..")
FOXDOT_TEMP_FILE = os.path.realpath(FOXDOT_EDITOR_ROOT + "/tmp/tempfile.txt")

# If the tempfile doesn't exist, create it
if not os.path.isfile(FOXDOT_TEMP_FILE):
    try:
        with open(FOXDOT_TEMP_FILE, "w") as f:
            pass
    except FileNotFoundError:
        pass

# Check for OS -> mac, linux, win
SYSTEM = 0
WINDOWS = 0
LINUX = 1
MAC_OS = 2

if sys.platform.startswith('darwin'):
    SYSTEM = MAC_OS
    # Attempted fix for some Mac OS users
    try:
        import matplotlib
        matplotlib.use('TkAgg')
    except ImportError:
        pass
elif sys.platform.startswith('win'):
    SYSTEM = WINDOWS
elif sys.platform.startswith('linux'):
    SYSTEM = LINUX