from pathlib import Path
from .settings_manager import settings
from .supercollider_settings import get_synthdefs_dir_path

import os

RENARDO_ROOT_PATH = str(Path(__file__).parent.parent)

SUPERCOLLIDER = ""
BOOT_ON_STARTUP = False

SC3_PLUGINS = False
MAX_CHANNELS = 2
SAMPLES_DIR = ""
SAMPLES_PACK_NUMBER = 0
GET_SC_INFO = True


CPU_USAGE = 2  # 0=low, 1=medium, 2=high
CLOCK_LATENCY = 0  # 0=low, 1=medium, 2=high

LOOP_DIR_NAME = "_loop_"
TUTORIAL_DIR = os.path.realpath(RENARDO_ROOT_PATH + "/lib/demo/")
RECORDING_DIR = os.path.realpath(RENARDO_ROOT_PATH + "/lib/rec/")

PERFORMANCE_EXCEPTIONS_CATCHING = True

FOXDOT_STARTUP_PATH = os.path.realpath(RENARDO_ROOT_PATH + "/Custom/startup.py")

# Directory for permanent/externally managed .scd file for synths
# (not overwritten)
SYNTHDEF_DIR = str(get_synthdefs_dir_path() / "scsynth")
# Directory to write temporary Python generated or Live sclang .scd synths
# To avoid overwriting permanent (default) synthdef scd files
TMP_SYNTHDEF_DIR = str(get_synthdefs_dir_path() / "tmp_code" / "scsynth")
EFFECTS_DIR = str(get_synthdefs_dir_path() / "sceffects")
TMP_EFFECTS_DIR = str(get_synthdefs_dir_path() / "tmp_code" / "sceffects")
ENVELOPE_DIR = str(get_synthdefs_dir_path() / "scenvelopes")
FOXDOT_EFFECTS_FILE = str(get_synthdefs_dir_path() / "Effects.scd")

# def GET_SYNTHDEF_FILES():
#    return [os.path.realpath(SYNTHDEF_DIR + "/" + path) for path in os.listdir(SYNTHDEF_DIR)]


# def GET_FX_FILES():
#    return [os.path.realpath(EFFECTS_DIR + "/" + path) for path in os.listdir(EFFECTS_DIR)]


def get_tutorial_files():
    return [os.path.realpath(TUTORIAL_DIR + "/" + path) for path in sorted(os.listdir(TUTORIAL_DIR))]

# settings.set_defaults_from_dict({
#     "TUTORIAL_DIR": str(TUTORIAL_DIR),
#     "FOXDOT_INFO_FILE": str(SCLANG_DIR_PATH / "Info.scd"),
#     "FOXDOT_RECORD_FILE" : str(SCLANG_DIR_PATH / "Record.scd"),
#     "FOXDOT_STARTUP_FILE" : str(SCLANG_DIR_PATH / "Startup.scd"),
#     "FOXDOT_OSC_FUNC" : str(SCLANG_DIR_PATH / "OSCFunc.scd"),
#     "FOXDOT_BUFFERS_FILE" : str(SCLANG_DIR_PATH / "Buffers.scd"),
#     "RECORDING_DIR" : str(Path(settings.get("RENARDO_USER_DIR")) / "rec"),
#     "OSC_MIDI_ADDRESS" : "/foxdot_midi",
#     "GET_SC_INFO" : True,
#     "ADDRESS" : 'localhost',
#     "PORT" : 57110,
#     "PORT2" : 57120,
#     "FORWARD_PORT" : 0,
#     "FORWARD_ADDRESS" : '',
# },
# internal=True
# )
