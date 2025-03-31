import os
from pathlib import Path
from renardo.gatherer import  get_user_config_dir_path
from renardo.sc_backend.settings_manager import SettingsManager


# Define default settings
public_defaults = {
    "app": {
        "name": "MyApp",
        "version": "1.0.0",
        "theme": "light",
        "window": {
            "width": 800,
            "height": 600
        }
    }
}

internal_defaults = {
    "user": {
        "api_key": "",
        "credentials": {
            "username": "",
            "password": ""
        }
    },
    "server": {
        "host": "localhost",
        "port": 8080
    }
}

# Create settings manager
supercollider_settings = SettingsManager(
    public_file=get_user_config_dir_path() / "sc_settings.toml",
    internal_file=Path("internal_sc_settings.toml"),
    public_defaults=public_defaults,
    internal_defaults=internal_defaults,
)

# TODO migrate all params to TOML settings and rename params

# TODO move this method to user config and renardo_gatherer when synthdef
# download implemented

ADDRESS = 'localhost'
PORT = 57110
PORT2 = 57120
FORWARD_PORT = 0
FORWARD_ADDRESS = ''

def get_synthdefs_dir_path():
    return get_user_config_dir_path() / 'sclang_code'

# OSC Information
OSC_MIDI_ADDRESS = "/foxdot_midi"
GET_SC_INFO = True

FOXDOT_INFO_FILE = str(get_synthdefs_dir_path() / "Info.scd")
FOXDOT_RECORD_FILE = str(get_synthdefs_dir_path() / "Record.scd")
FOXDOT_STARTUP_FILE = str(get_synthdefs_dir_path() / "Startup.scd")
FOXDOT_OSC_FUNC = str(get_synthdefs_dir_path() / "OSCFunc.scd")
FOXDOT_BUFFERS_FILE = str(get_synthdefs_dir_path() / "Buffers.scd")

RECORDING_DIR = (get_user_config_dir_path() / "rec")
RECORDING_DIR.mkdir(exist_ok=True)
