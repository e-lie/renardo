import os, sys, json
from pathlib import Path

from .settings_manager import settings


TEMP_FILE : Path = settings.get_path("FOXDOT_EDITOR_ROOT") / "tmp" / "tempfile.txt"
TEMP_FILE.touch(exist_ok=True)

settings.set_defaults_from_dict({
    "foxdot_editor" : {
        "TEMP_FILE": "tmp/tempfile.txt",
        "FONT": 'Consolas',
        "AUTO_COMPLETE_BRACKETS": True,
        "USE_ALPHA": True,
        "ALPHA_VALUE": 0.8,
        "MENU_ON_STARTUP": True,
        "CONSOLE_ON_STARTUP": True,
        "LINENUMBERS_ON_STARTUP": True,
        "TREEVIEW_ON_STARTUP": False,
        "TRANSPARENT_ON_STARTUP": False,
        "RECOVER_WORK": True,
        "LINE_NUMBER_MARKER_OFFSET": 0,
        "CHECK_FOR_UPDATE": True,
        "COLOR_THEME": 'cyborg',
        "TEXT_COLORS": 'default',
    }
},
)

settings.set_defaults_from_dict({
    "foxdot_editor" : {
        "ICON":  "img/icon.ico",
        "ICON_GIF": "img/icon.gif",
        "THEMES_PATH": "themes",
    }
},
internal=True
)

conf = {}

TEXT_COLORS = settings.get("foxdot_editor.TEXT_COLORS")
theme_file_path = Path(settings.get("foxdot_editor.THEMES_PATH")) / f"{TEXT_COLORS}.json"

try:

    file = Path(settings.get("foxdot_editor.THEMES_PATH")) / f"{TEXT_COLORS}.json"
    # Opening JSON file
    with open(file, 'r') as openfile:
        # Reading from json file
        json_object = json.load(openfile)
        # Text area colours
        # ------------------
        conf["plaintext"] = json_object[TEXT_COLORS]['plaintext']
        conf["background"] = json_object[TEXT_COLORS]['background']
        conf["functions"] = json_object[TEXT_COLORS]['functions']
        conf["key_types"] = json_object[TEXT_COLORS]['key_types']
        conf["user_defn"] = json_object[TEXT_COLORS]['user_defn']
        conf["other_kws"] = json_object[TEXT_COLORS]['other_kws']
        conf["comments"] = json_object[TEXT_COLORS]['comments']
        conf["numbers"] = json_object[TEXT_COLORS]['numbers']
        conf["strings"] = json_object[TEXT_COLORS]['strings']
        conf["dollar"] = json_object[TEXT_COLORS]['dollar']
        conf["arrow"] = json_object[TEXT_COLORS]['arrow']
        conf["players"] = json_object[TEXT_COLORS]['players']
        # Prompt colours
        # ------------------
        conf["prompt_fg"] = json_object[TEXT_COLORS]['prompt_fg']
        conf["prompt_bg"] = json_object[TEXT_COLORS]['prompt_bg']
        # Console area colours
        # ------------------
        conf["console_text"] = json_object[TEXT_COLORS]['console_text']
        conf["console_bg"] = json_object[TEXT_COLORS]['console_bg']

except FileNotFoundError:
    print(f"{theme_file_path} color config file not found! Use default values instead.")
    # Text area colours
    # ------------------
    conf["plaintext"] = '#ffffff'
    conf["background"] = '#1a1a1a'
    conf["functions"] = '#bf4acc'
    conf["key_types"] = '#29abe2'
    conf["user_defn"] = '#29abe2'
    conf["other_kws"] = '#49db8b'
    conf["comments"] = '#666666'
    conf["numbers"] = '#e89c18'
    conf["strings"] = '#eae02a'
    conf["dollar"] = '#ec4e20'
    conf["arrow"] = '#eae02a'
    conf["players"] = '#ec4e20'
    # Prompt colours
    # ------------------
    conf["prompt_fg"] = '#4d4d4d'
    conf["prompt_bg"] = '#666666'
    # Console area colours
    # ------------------
    conf["console_text"] = '#ffffff'
    conf["console_bg"] = '#000000'

# Sound category colours
# ------------------
conf["kick"] = '#780373'
conf["various"] = '#ffbf00'
conf["vocal"] = '#ffa6a6'
conf["bell"] = '#158466'
conf["hihat"] = '#81d41a'
conf["clap"] = '#729fcf'
conf["snap"] = '#729fcf'
conf["shaker"] = '#a7074b'
conf["tambourine"] = '#a7074b'
conf["crash"] = '#bbe33d'
conf["cymbal"] = '#bbe33d'
conf["soundfx"] = '#3465a4'
conf["tom"] = '#ff3838'
conf["noise"] = '#6b5e9b'
conf["ride"] = '#ffffa6'
conf["perc"] = '#ff8000'
conf["snare"] = '#ffff38'
conf["rim"] = '#ffff38'
conf["loops"] = '#1e1e19'
conf["default"] = '#b2b2b2'
conf["text1"] = '#ffffff'
conf["text2"] = '#000000'

# Loading from env
# ------------------
for key, value in os.environ.items():
    if key in conf:
        conf[key] = value

# Colours
class Colours:
    # Text area colours
    plaintext = conf["plaintext"]
    background = conf["background"]
    functions = conf["functions"]
    key_types = conf["key_types"]
    user_defn = conf["user_defn"]
    other_kws = conf["other_kws"]
    comments = conf["comments"]
    numbers = conf["numbers"]
    strings = conf["strings"]
    dollar = conf["dollar"]
    arrow = conf["arrow"]
    players = conf["players"]
    prompt_fg = conf["prompt_fg"]
    prompt_bg = conf["prompt_bg"]
    # Console area colours
    console_text = conf["console_text"]
    console_bg = conf["console_bg"]
    # Sample chart colours
    kick = conf["kick"]
    various = conf["various"]
    vocal = conf["vocal"]
    bell = conf["bell"]
    hihat = conf["hihat"]
    clap = conf["clap"]
    snap = conf["snap"]
    shaker = conf["shaker"]
    tambourine = conf["tambourine"]
    crash = conf["crash"]
    cymbal = conf["cymbal"]
    soundfx = conf["soundfx"]
    tom = conf["tom"]
    noise = conf["noise"]
    ride = conf["ride"]
    perc = conf["perc"]
    snare = conf["snare"]
    rim = conf["rim"]
    loops = conf["loops"]
    default = conf["default"]
    text1 = conf["text1"]
    text2 = conf["text2"]
