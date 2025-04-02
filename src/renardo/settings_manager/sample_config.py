from pathlib import Path
from .config_dir import DEFAULT_SAMPLES_PACK_NAME, LOOP_SUBDIR
from .settings_manager import settings

def default_loop_path() -> Path:
    return Path(settings.get("SAMPLES_DIR")) / DEFAULT_SAMPLES_PACK_NAME / LOOP_SUBDIR

alpha    = "abcdefghijklmnopqrstuvwxyz"
nonalpha = {"&": "_ampersand",
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
            "9": "9"}