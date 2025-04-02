import os
from pathlib import Path
from .settings_manager import settings
# from .. import SYNTHDEF_DIR

ADDRESS = 'localhost'
PORT = 57110
PORT2 = 57120
FORWARD_PORT = 0
FORWARD_ADDRESS = ''

def get_synthdefs_dir_path():
    return Path(settings.get("RENARDO_USER_DIR")) / 'sclang_code'

# OSC Information
OSC_MIDI_ADDRESS = "/foxdot_midi"
GET_SC_INFO = True

FOXDOT_INFO_FILE = str(get_synthdefs_dir_path() / "Info.scd")
FOXDOT_RECORD_FILE = str(get_synthdefs_dir_path() / "Record.scd")
FOXDOT_STARTUP_FILE = str(get_synthdefs_dir_path() / "Startup.scd")
FOXDOT_OSC_FUNC = str(get_synthdefs_dir_path() / "OSCFunc.scd")
FOXDOT_BUFFERS_FILE = str(get_synthdefs_dir_path() / "Buffers.scd")

RECORDING_DIR = Path(settings.get("RENARDO_USER_DIR")) / "rec"
RECORDING_DIR.mkdir(exist_ok=True)


SCLANG_DIR_PATH = Path(settings.get("RENARDO_USER_DIR")) / 'sclang_code'

settings.set_defaults_from_dict({
    "SCLANG_CODE_DIR_PATH": str(SCLANG_DIR_PATH),
    "FOXDOT_INFO_FILE": str(SCLANG_DIR_PATH / "Info.scd"),
    "FOXDOT_RECORD_FILE" : str(SCLANG_DIR_PATH / "Record.scd"),
    "FOXDOT_STARTUP_FILE" : str(SCLANG_DIR_PATH / "Startup.scd"),
    "FOXDOT_OSC_FUNC" : str(SCLANG_DIR_PATH / "OSCFunc.scd"),
    "FOXDOT_BUFFERS_FILE" : str(SCLANG_DIR_PATH / "Buffers.scd"),
    "RECORDING_DIR" : str(Path(settings.get("RENARDO_USER_DIR")) / "rec"),
    "OSC_MIDI_ADDRESS" : "/foxdot_midi",
    "GET_SC_INFO" : True,
    "ADDRESS" : 'localhost',
    "PORT" : 57110,
    "PORT2" : 57120,
    "FORWARD_PORT" : 0,
    "FORWARD_ADDRESS" : '',
},
internal=True
)



settings.save_to_file()