from pathlib import Path
from .supercollider_settings import get_synthdefs_dir_path

FOXDOT_ROOT = str(Path(__file__).parent.parent)

ADDRESS = 'localhost'
PORT = 57110
PORT2 = 57120

SUPERCOLLIDER = ""
BOOT_ON_STARTUP = False

SC3_PLUGINS = False
MAX_CHANNELS = 2
SAMPLES_DIR = ""
SAMPLES_PACK_NUMBER = 0
GET_SC_INFO = True


CPU_USAGE = 2  # 0=low, 1=medium, 2=high
CLOCK_LATENCY = 0  # 0=low, 1=medium, 2=high
FORWARD_ADDRESS = ''
FORWARD_PORT = 0

FOXDOT_SND = get_samples_dir_path()
FOXDOT_LOOP = "_loop_"
TUTORIAL_DIR = os.path.realpath(FOXDOT_ROOT + "/lib/demo/")
RECORDING_DIR = os.path.realpath(FOXDOT_ROOT + "/lib/rec/")

PERFORMANCE_EXCEPTIONS_CATCHING = True

FOXDOT_STARTUP_PATH = os.path.realpath(FOXDOT_ROOT + "/Custom/startup.py")

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
