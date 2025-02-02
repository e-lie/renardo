import os
import pathlib
from sys import platform

USER_CONFIG_DIR_PATH = None

# default config path
# on windows AppData/Roaming/renardo
# on Linux ~/.config/renardo
# on MacOS /Users/<username>/Library/Application Support/renardo
if platform == "linux" or platform == "linux2" :
    home_path = pathlib.Path.home()
    USER_CONFIG_DIR_PATH = home_path / '.config' / 'renardo'
elif platform == "darwin":
    home_path = pathlib.Path.home()
    USER_CONFIG_DIR_PATH = home_path / 'Library' / 'Application Support' / 'renardo'
elif platform == "win32":
    appdata_roaming_path = pathlib.Path(os.getenv('APPDATA'))
    USER_CONFIG_DIR_PATH = appdata_roaming_path / 'renardo'


def get_samples_dir_path():
    return USER_CONFIG_DIR_PATH / 'samples'