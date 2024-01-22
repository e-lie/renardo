import os
import pathlib
from sys import platform

SAMPLES_DIR_PATH = None

# default config path
# on windows AppData/Roaming/renardo
# on Linux ~/.config/renardo
# on MacOS /Users/<username>/Library/Application Support/renardo
if platform == "linux" or platform == "linux2" :
    home_path = pathlib.Path.home()
    SAMPLES_DIR_PATH = home_path / '.config' / 'renardo' / 'samples'
elif platform == "darwin":
    home_path = pathlib.Path.home()
    SAMPLES_DIR_PATH = home_path / 'Library' / 'Application Support' / 'renardo' / 'samples'
elif platform == "win32":
    appdata_roaming_path = pathlib.Path(os.getenv('APPDATA'))
    SAMPLES_DIR_PATH = appdata_roaming_path / 'renardo' / 'samples'


