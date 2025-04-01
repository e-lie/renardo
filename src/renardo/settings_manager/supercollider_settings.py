import os
from pathlib import Path
from .settings_manager import settings_manager


ADDRESS = 'localhost'
PORT = 57110
PORT2 = 57120
FORWARD_PORT = 0
FORWARD_ADDRESS = ''

def get_synthdefs_dir_path():
    return Path(settings_manager.get("RENARDO_USER_DIR")) / 'sclang_code'

# OSC Information
OSC_MIDI_ADDRESS = "/foxdot_midi"
GET_SC_INFO = True

FOXDOT_INFO_FILE = str(get_synthdefs_dir_path() / "Info.scd")
FOXDOT_RECORD_FILE = str(get_synthdefs_dir_path() / "Record.scd")
FOXDOT_STARTUP_FILE = str(get_synthdefs_dir_path() / "Startup.scd")
FOXDOT_OSC_FUNC = str(get_synthdefs_dir_path() / "OSCFunc.scd")
FOXDOT_BUFFERS_FILE = str(get_synthdefs_dir_path() / "Buffers.scd")

RECORDING_DIR = Path(settings_manager.get("RENARDO_USER_DIR")) / "rec"
RECORDING_DIR.mkdir(exist_ok=True)
