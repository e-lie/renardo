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
    return USER_CONFIG_DIR_PATH / 'sample_packs'

def get_user_config_dir_path():
    return USER_CONFIG_DIR_PATH


SAMPLES_DIR_PATH = get_samples_dir_path()
DEFAULT_SAMPLES_PACK_NAME = '0_foxdot_default'
# DEFAULT_SAMPLES_PACK_NAME = '0_foxdot_default_testing'
LOOP_SUBDIR = '_loop_'

SAMPLES_DOWNLOAD_SERVER = 'https://collections.renardo.org/sample_packs'

DESCRIPTIONS = { 'a' : "Gameboy hihat",      'A' : "Gameboy kick drum",
                 'b' : "Noisy beep",         'B' : "Short saw",
                 'c' : "Voice/string",       'C' : "Choral",
                 'd' : "Woodblock",          'D' : "Dirty snare",
                 'e' : "Electronic Cowbell", 'E' : "Ringing percussion",
                 'f' : "Pops",               'F' : "Trumpet stabs",
                 'g' : "Ominous",            'G' : "Ambient stabs",
                 'h' : "Finger snaps",       'H' : "Clap",
                 'i' : "Jungle snare",       'I' : "Rock snare",
                 'j' : "Whines",             'J' : "Ambient stabs",
                 'k' : "Wood shaker",        'K' : "Percussive hits",
                 'l' : "Robot noise",        'L' : "Noisy percussive hits",
                 'm' : "808 toms",           'M' : "Acoustic toms",
                 'n' : "Noise",              'N' : "Gameboy SFX",
                 'o' : "Snare drum",         'O' : "Heavy snare",
                 'p' : "Tabla",              'P' : "Tabla long",
                 'q' : "Ambient stabs",      'Q' : "Electronic stabs",
                 'r' : "Metal",              'R' : "Metallic",
                 's' : "Shaker",             'S' : "Tamborine",
                 't' : "Rimshot",            'T' : "Cowbell",
                 'u' : "Soft snare",         'U' : "Misc. Fx",
                 'v' : "Soft kick",          'V' : "Hard kick",
                 'w' : "Dub hits",           'W' : "Distorted",
                 'x' : "Bass drum",          'X' : "Heavy kick",
                 'y' : "Percussive hits",    'Y' : "High buzz",
                 'z' : "Scratch",            "Z" : "Loud stabs",
                 '-' : "Hi hat closed",      "|" : "Hangdrum",
                 '=' : "Hi hat open",        "/" : "Reverse sounds",
                 '*' : "Clap",               "\\" : "Lazer",
                 '~' : "Ride cymbal",        "%" : "Noise bursts",
                 '^' : "'Donk'",             "$" : "Beatbox",
                 '#' : "Crash",              "!" : "Yeah!",
                 '+' : "Clicks",             "&" : "Chime",
                 '@' : "Gameboy noise",      ":" : "Hi-hats",
                 '1' : "Vocals (One)",
                 '2' : 'Vocals (Two)',
                 '3' : 'Vocals (Three)',
                 '4' : 'Vocals (Four)'}