import os
import sys
import pathlib

# Anything that needs to be updated

from importlib import reload
from renardo_gatherer.config_dir import get_samples_dir_path

# Check for OS -> mac, linux, win

SYSTEM  = 0
WINDOWS = 0
LINUX   = 1
MAC_OS  = 2

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

# Directory informations

USER_CWD     = os.path.realpath(".")
FOXDOT_ROOT  = os.path.realpath(__file__ + "/../../")
FOXDOT_ICON  = os.path.realpath(FOXDOT_ROOT + "/Workspace/img/icon.ico")
FOXDOT_ICON_GIF = os.path.realpath(FOXDOT_ROOT + "/Workspace/img/icon.gif")
FOXDOT_HELLO = os.path.realpath(FOXDOT_ROOT + "/Workspace/img/hello.txt")
FOXDOT_STARTUP_PATH = os.path.realpath(FOXDOT_ROOT + "/Custom/startup.py")
# FOXDOT_SND = SAMPLES_FOLDER_PATH / 'foxdot_default'
FOXDOT_SND = get_samples_dir_path()
# FOXDOT_LOOP = SAMPLES_FOLDER_PATH / 'foxdot_default' / '_loop_'
FOXDOT_LOOP  = "_loop_"
# FOXDOT_LOOP  = os.path.realpath(FOXDOT_ROOT + "/../../renardo_samples/_loop_/")

TUTORIAL_DIR  = os.path.realpath(FOXDOT_ROOT + "/demo/")
RECORDING_DIR = os.path.realpath(FOXDOT_ROOT + "/rec/")
FOXDOT_TEMP_FILE    = os.path.realpath(FOXDOT_ROOT + "/Workspace/tmp/tempfile.txt")

SCLANG_EXEC   = 'sclang.exe' if SYSTEM == WINDOWS else 'sclang'


# TODO move this method to user config and renardo_gatherer when synthdef download implemented
def get_synthdefs_dir_path():
    return pathlib.Path(FOXDOT_ROOT) / 'SynthDefManagement' / 'sclang_code'

# Directory for permanent/externally managed .scd file for synths (not overwritten)
SYNTHDEF_DIR = str(get_synthdefs_dir_path() / "scsynth")

# Directory to write temporary Python generated or Live sclang .scd synths
# To avoid overwriting permanent (default) synthdef scd files
TMP_SYNTHDEF_DIR = str(get_synthdefs_dir_path() / "tmp_code" / "scsynth")

EFFECTS_DIR = str(get_synthdefs_dir_path() / "sceffects")
TMP_EFFECTS_DIR = str(get_synthdefs_dir_path() / "tmp_code" / "sceffects")

ENVELOPE_DIR = str(get_synthdefs_dir_path() / "scenvelopes")
FOXDOT_OSC_FUNC = str(get_synthdefs_dir_path() / "OSCFunc.scd")
FOXDOT_STARTUP_FILE = str(get_synthdefs_dir_path() / "Startup.scd")
FOXDOT_BUFFERS_FILE = str(get_synthdefs_dir_path() / "Buffers.scd")
FOXDOT_EFFECTS_FILE = str(get_synthdefs_dir_path() / "Effects.scd")
FOXDOT_INFO_FILE = str(get_synthdefs_dir_path() / "Info.scd")
FOXDOT_RECORD_FILE  = str(get_synthdefs_dir_path() / "Record.scd")

# If the tempfile doesn't exist, create it

if not os.path.isfile(FOXDOT_TEMP_FILE):
    try:
        with open(FOXDOT_TEMP_FILE, "w") as f:
            pass
    except FileNotFoundError:
        pass

#def GET_SYNTHDEF_FILES():
#    return [os.path.realpath(SYNTHDEF_DIR + "/" + path) for path in os.listdir(SYNTHDEF_DIR)]
#
#def GET_FX_FILES():
#    return [os.path.realpath(EFFECTS_DIR + "/" + path) for path in os.listdir(EFFECTS_DIR)]

def GET_TUTORIAL_FILES():
    return [os.path.realpath(TUTORIAL_DIR + "/" + path) for path in sorted(os.listdir(TUTORIAL_DIR))]

# Set Environment Variables

try:
    reload(conf) # incase of a reload
except NameError:
    from renardo_lib.Settings import conf

FOXDOT_CONFIG_FILE  = conf.filename
    
ADDRESS                   = conf.ADDRESS
PORT                      = conf.PORT
PORT2                     = conf.PORT2
FONT                      = conf.FONT
SC3_PLUGINS               = conf.SC3_PLUGINS
MAX_CHANNELS              = conf.MAX_CHANNELS
GET_SC_INFO               = conf.GET_SC_INFO
USE_ALPHA                 = conf.USE_ALPHA
ALPHA_VALUE               = conf.ALPHA_VALUE
MENU_ON_STARTUP           = conf.MENU_ON_STARTUP
TRANSPARENT_ON_STARTUP    = conf.TRANSPARENT_ON_STARTUP
RECOVER_WORK              = conf.RECOVER_WORK
CHECK_FOR_UPDATE          = conf.CHECK_FOR_UPDATE
LINE_NUMBER_MARKER_OFFSET = conf.LINE_NUMBER_MARKER_OFFSET
AUTO_COMPLETE_BRACKETS    = conf.AUTO_COMPLETE_BRACKETS
CPU_USAGE                 = conf.CPU_USAGE
CLOCK_LATENCY             = conf.CLOCK_LATENCY
FORWARD_ADDRESS           = conf.FORWARD_ADDRESS
FORWARD_PORT              = conf.FORWARD_PORT
SAMPLES_PACK_NUMBER       = conf.SAMPLES_PACK_NUMBER

if conf.SAMPLES_DIR is not None and conf.SAMPLES_DIR != "":

    FOXDOT_SND = os.path.realpath(conf.SAMPLES_DIR)

def get_timestamp():
    import time
    return time.strftime("%Y%m%d-%H%M%S")

# Name of SamplePlayer and LoopPlayer SynthDef

class _SamplePlayer:
    names = ('play1', 'play2',)
    def __eq__(self, other):
        return other in self.names
    def __ne__(self, other):
        return other not in self.names

class _LoopPlayer:
    names = ("loop", "gsynth", 'stretch')
    def __eq__(self, other):
        return other in self.names
    def __ne__(self, other):
        return other not in self.names

class _MidiPlayer:
    name = "MidiOut"
    def __eq__(self, other):
        return other == self.name
    def __ne__(self, other):
        return other != self.name

SamplePlayer = _SamplePlayer()
LoopPlayer   = _LoopPlayer()
MidiPlayer   = _MidiPlayer()


# OSC Information

OSC_MIDI_ADDRESS = "/foxdot_midi"

# Colours

class COLOURS:
    plaintext       = conf.plaintext
    background      = conf.background
    functions       = conf.functions
    key_types       = conf.key_types
    user_defn       = conf.user_defn
    other_kws       = conf.other_kws
    comments        = conf.comments
    numbers         = conf.numbers
    strings         = conf.strings
    dollar          = conf.dollar
    arrow           = conf.arrow
    players         = conf.players
    kick            = conf.kick
    various         = conf.various
    vocal           = conf.vocal
    bell            = conf.bell
    hihat           = conf.hihat
    clap            = conf.clap
    snap            = conf.snap
    shaker          = conf.shaker
    tambourine       = conf.tambourine
    crash           = conf.crash
    cymbal          = conf.cymbal
    soundfx         = conf.soundfx
    tom             = conf.tom
    noise           = conf.noise
    ride            = conf.ride
    perc            = conf.perc
    snare           = conf.snare
    rim             = conf.rim
    loops           = conf.loops
    default         = conf.default
    text1           = conf.text1
    text2           = conf.text2
