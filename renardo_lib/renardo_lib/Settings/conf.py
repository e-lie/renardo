import os.path
import json
from renardo_lib.Settings import FOXDOT_EDITOR_THEMES

# Settings
# ------------------
ADDRESS = 'localhost'
PORT = 57110
PORT2 = 57120
FONT = 'Consolas'
SUPERCOLLIDER = ""
BOOT_ON_STARTUP = False
CHECK_FOR_UPDATE = True
SC3_PLUGINS = False
MAX_CHANNELS = 2
SAMPLES_DIR = ""
SAMPLES_PACK_NUMBER = 0
GET_SC_INFO = True
USE_ALPHA = True
ALPHA_VALUE = 0.8
MENU_ON_STARTUP = True
CONSOLE_ON_STARTUP = True
LINENUMBERS_ON_STARTUP = True
TREEVIEW_ON_STARTUP = False
MIDIBAR_ON_STARTUP = False
TRANSPARENT_ON_STARTUP = False
RECOVER_WORK = True
LINE_NUMBER_MARKER_OFFSET = 0
AUTO_COMPLETE_BRACKETS = True
CPU_USAGE = 2  # 0=low, 1=medium, 2=high
CLOCK_LATENCY = 0  # 0=low, 1=medium, 2=high
FORWARD_ADDRESS = ''
FORWARD_PORT = 0
COLOR_THEME = 'vapor'

# Loading from file
# ------------------
filename = os.path.join(os.path.dirname(__file__), "conf.json")
try:
    with open(filename, 'r') as file:
        settings = json.load(file)
        locals().update(settings)
        file.close()
except FileNotFoundError:
    print("Could not read conf.json file. New conf.json from default values created!")
    settings = {}
    settings["ADDRESS"] = 'localhost'
    settings["PORT"] = 57110
    settings["PORT2"] = 57120
    settings["FONT"] = 'Consolas'
    settings["SUPERCOLLIDER"] = ''
    settings["BOOT_ON_STARTUP"] = False
    settings["CHECK_FOR_UPDATE"] = True
    settings["SC3_PLUGINS"] = False
    settings["MAX_CHANNELS"] = 2
    settings["SAMPLES_DIR"] = ''
    settings["SAMPLES_PACK_NUMBER"] = 0
    settings["GET_SC_INFO"] = True
    settings["USE_ALPHA"] = True
    settings["ALPHA_VALUE"] = 0.8
    settings["MENU_ON_STARTUP"] = True
    settings["CONSOLE_ON_STARTUP"] = True
    settings["LINENUMBERS_ON_STARTUP"] = True
    settings["TREEVIEW_ON_STARTUP"] = False
    settings["MIDIBAR_ON_STARTUP"] = False
    settings["TRANSPARENT_ON_STARTUP"] = False
    settings["RECOVER_WORK"] = True
    settings["LINE_NUMBER_MARKER_OFFSET"] = 0
    settings["AUTO_COMPLETE_BRACKETS"] = True
    settings["CPU_USAGE"] = 2
    settings["CLOCK_LATENCY"] = 0
    settings["FORWARD_ADDRESS"] = ''
    settings["FORWARD_PORT"] = 0
    settings["COLOR_THEME"] = 'vapor'
    # Write Settings into json file
    filename = os.path.join(os.path.dirname(__file__), "conf.json")
    try:
        settings_file = open(filename, "w")
        json.dump(settings, settings_file, indent=6)
        settings_file.close()
    except Exception:
        print("Could not write conf.json settings file! Create conf.json from default values!")


try:
    # Opening JSON file
    with open(FOXDOT_EDITOR_THEMES, 'r') as openfile:
        # Reading from json file
        json_object = json.load(openfile)
        # Text area colours
        # ------------------
        for item in json_object["themes"]:
            if COLOR_THEME in item:
                plaintext = item[COLOR_THEME]["colors"]["fg"]
                background = item[COLOR_THEME]["colors"]["bg"]
                functions = item[COLOR_THEME]["colors"]["secondary"]
                key_types = item[COLOR_THEME]["colors"]["info"]
                user_defn = item[COLOR_THEME]["colors"]["success"]
                other_kws = item[COLOR_THEME]["colors"]["success"]
                comments = item[COLOR_THEME]["colors"]["light"]
                numbers = item[COLOR_THEME]["colors"]["secondary"]
                strings = item[COLOR_THEME]["colors"]["warning"]
                dollar = item[COLOR_THEME]["colors"]["active"]
                arrow = item[COLOR_THEME]["colors"]["warning"]
                players = item[COLOR_THEME]["colors"]["danger"]
                # Prompt colours
                # ------------------
                prompt_fg = item[COLOR_THEME]["colors"]["selectfg"]
                prompt_bg = item[COLOR_THEME]["colors"]["selectbg"]
                # Console area colours
                # ------------------
                console_text = item[COLOR_THEME]["colors"]["inputfg"]
                console_bg = item[COLOR_THEME]["colors"]["inputbg"]
except FileNotFoundError:
    print(f"{FOXDOT_EDITOR_THEMES}: File not found! Use default values instead.")
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
snare = '#f9e644'
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
