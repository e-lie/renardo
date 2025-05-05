from pathlib import Path
from .settings_manager import settings

settings.set_defaults_from_dict(
{
    "samples" : {
        "SAMPLES_PACK_NUMBER": 0,
    }
})


settings.set_defaults_from_dict(
{
    "samples" : {
        "MAX_CHANNELS": 2,
        "LOOP_DIR_NAME": "_loop_",
        "DEFAULT_SAMPLE_PACK_NAME": '0_foxdot_default',
        # "DEFAULT_SAMPLES_PACK_NAME": '0_foxdot_default_testing',
        "SAMPLES_DIR_NAME": 'sample_packs',
        "ALPHA": "abcdefghijklmnopqrstuvwxyz",
        "NON_ALPHA": {"&": "_ampersand",
                    "*": "_asterix",
                    "@": "_at",
                    "\\": "_backslash",
                    "|": "_bar",
                    "^": "_caret",
                    ":": "_colon",
                    "$": "_dollar",
                    "=": "_equals",
                    "!": "_exclamation",
                    "/": "_forwardslash",
                    "#": "_hash",
                    "-": "_hyphen",
                    "<": "_lessthan",
                    "%": "_percent",
                    "+": "_plus",
                    "?": "_question",
                    ";": "_semicolon",
                    "~": "_tilde",
                    ",": "_comma",
                    "0": "0",
                    "1": "1",
                    "2": "2",
                    "3": "3",
                    "4": "4",
                    "5": "5",
                    "6": "6",
                    "7": "7",
                    "8": "8",
                    "9": "9"},
        "SYMBOLS_DESCRIPTION": { 'a' : "Gameboy hihat",      'A' : "Gameboy kick drum",
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
        }
    },
    internal=True
)

settings.save_to_file()
