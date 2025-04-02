from pathlib import Path
from .settings_manager import settings

import os

RENARDO_ROOT_PATH = Path(__file__).parent.parent

settings.set_defaults_from_dict({
    "core": {
        "RENARDO_ROOT_PATH": str(RENARDO_ROOT_PATH),
        "TUTORIAL_DIR": str(RENARDO_ROOT_PATH / "lib" / "demo" ),
        "STARTUP_FILE_PATH" : str(RENARDO_ROOT_PATH / "Custom" / "startup.py"),
        "PERFORMANCE_EXCEPTIONS_CATCHING" : True,
        "CPU_USAGE" : 2,
        "CLOCK_LATENCY" : 0,
    }
},
internal=True
)

settings.save_to_file()

def get_tutorial_files():
    return [
        str(Path(settings.get("TUTORIAL_DIR")) / path)
        for path in sorted(os.listdir(settings.get("TUTORIAL_DIR")))
    ]