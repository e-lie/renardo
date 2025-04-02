import os, sys, json

from .foxdot_config import RENARDO_ROOT_PATH

FOXDOT_EDITOR_ROOT = os.path.realpath(RENARDO_ROOT_PATH + "/foxdot_editor")
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


FOXDOT_EDITOR_ROOT = RENARDO_ROOT_PATH + "/foxdot_editor"

FOXDOT_ICON = os.path.realpath(FOXDOT_EDITOR_ROOT + "/img/icon.ico")
FOXDOT_ICON_GIF = os.path.realpath(FOXDOT_EDITOR_ROOT + "/img/icon.gif")
FOXDOT_HELLO = os.path.realpath(FOXDOT_EDITOR_ROOT + "/img/hello.txt")

FONT = 'Consolas'
AUTO_COMPLETE_BRACKETS = True
USE_ALPHA = True
ALPHA_VALUE = 0.8
MENU_ON_STARTUP = True
CONSOLE_ON_STARTUP = True
LINENUMBERS_ON_STARTUP = True
TREEVIEW_ON_STARTUP = False
TRANSPARENT_ON_STARTUP = False
RECOVER_WORK = True
LINE_NUMBER_MARKER_OFFSET = 0
CHECK_FOR_UPDATE = True

COLOR_THEME = 'cyborg'
TEXT_COLORS = 'default'

FOXDOT_EDITOR_THEMES_PATH = os.path.realpath(FOXDOT_EDITOR_ROOT + "/themes")

conf = {}

try:
    file = FOXDOT_EDITOR_THEMES_PATH + '/' + TEXT_COLORS + '.json'
    # Opening JSON file
    with open(file, 'r') as openfile:
        # Reading from json file
        json_object = json.load(openfile)
        # Text area colours
        # ------------------
        plaintext = json_object[TEXT_COLORS]['plaintext']
        background = json_object[TEXT_COLORS]['background']
        functions = json_object[TEXT_COLORS]['functions']
        key_types = json_object[TEXT_COLORS]['key_types']
        user_defn = json_object[TEXT_COLORS]['user_defn']
        other_kws = json_object[TEXT_COLORS]['other_kws']
        comments = json_object[TEXT_COLORS]['comments']
        numbers = json_object[TEXT_COLORS]['numbers']
        strings = json_object[TEXT_COLORS]['strings']
        dollar = json_object[TEXT_COLORS]['dollar']
        arrow = json_object[TEXT_COLORS]['arrow']
        players = json_object[TEXT_COLORS]['players']
        # Prompt colours
        # ------------------
        prompt_fg = json_object[TEXT_COLORS]['prompt_fg']
        prompt_bg = json_object[TEXT_COLORS]['prompt_bg']
        # Console area colours
        # ------------------
        console_text = json_object[TEXT_COLORS]['console_text']
        console_bg = json_object[TEXT_COLORS]['console_bg']

except FileNotFoundError:
    print(f"{FOXDOT_EDITOR_THEMES_PATH + '/' + TEXT_COLORS + '.json'} color config file not found! Use default values instead.")
    # Text area colours
    # ------------------
    plaintext = '#ffffff'
    background = '#1a1a1a'
    functions = '#bf4acc'
    key_types = '#29abe2'
    user_defn = '#29abe2'
    other_kws = '#49db8b'
    comments = '#666666'
    numbers = '#e89c18'
    strings = '#eae02a'
    dollar = '#ec4e20'
    arrow = '#eae02a'
    players = '#ec4e20'
    # Prompt colours
    # ------------------
    prompt_fg = '#4d4d4d'
    prompt_bg = '#666666'
    # Console area colours
    # ------------------
    console_text = '#ffffff'
    console_bg = '#000000'

# Sound category colours
# ------------------
kick = '#780373'
various = '#ffbf00'
vocal = '#ffa6a6'
bell = '#158466'
hihat = '#81d41a'
clap = '#729fcf'
snap = '#729fcf'
shaker = '#a7074b'
tambourine = '#a7074b'
crash = '#bbe33d'
cymbal = '#bbe33d'
soundfx = '#3465a4'
tom = '#ff3838'
noise = '#6b5e9b'
ride = '#ffffa6'
perc = '#ff8000'
snare = '#ffff38'
rim = '#ffff38'
loops = '#1e1e19'
default = '#b2b2b2'
text1 = '#ffffff'
text2 = '#000000'

# Loading from env
# ------------------
for key, value in os.environ.items():
    if key in globals():
        globals()[key] = value

# Colours
class COLOURS:
    # Text area colours
    plaintext = conf.plaintext
    background = conf.background
    functions = conf.functions
    key_types = conf.key_types
    user_defn = conf.user_defn
    other_kws = conf.other_kws
    comments = conf.comments
    numbers = conf.numbers
    strings = conf.strings
    dollar = conf.dollar
    arrow = conf.arrow
    players = conf.players
    prompt_fg = conf.prompt_fg
    prompt_bg = conf.prompt_bg
    # Console area colours
    console_text = conf.console_text
    console_bg = conf.console_bg
    # Sample chart colours
    kick = conf.kick
    various = conf.various
    vocal = conf.vocal
    bell = conf.bell
    hihat = conf.hihat
    clap = conf.clap
    snap = conf.snap
    shaker = conf.shaker
    tambourine = conf.tambourine
    crash = conf.crash
    cymbal = conf.cymbal
    soundfx = conf.soundfx
    tom = conf.tom
    noise = conf.noise
    ride = conf.ride
    perc = conf.perc
    snare = conf.snare
    rim = conf.rim
    loops = conf.loops
    default = conf.default
    text1 = conf.text1
    text2 = conf.text2

