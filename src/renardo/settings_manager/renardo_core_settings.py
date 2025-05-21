from pathlib import Path
from .settings_manager import settings

import os



settings.set_defaults_from_dict({
    "core": {
        "INSTANCIATE_FOXDOT_PLAYERS": True,
        "STARTUP_FILE_NAME": "default.py",
    }
},
)

settings.set_defaults_from_dict({
    "core": {
        "CPU_USAGE" : 2,
        "CLOCK_LATENCY" : 0,
        "PERFORMANCE_EXCEPTIONS_CATCHING" : True,
        "COLLECTIONS_DOWNLOAD_SERVER": 'https://collections.renardo.org',
    }
},
internal=True
)

settings.save_to_file()

def get_tutorial_files():
    tutorial_dir = settings.get_path("RENARDO_ROOT_PATH") / "demo"
    return [
        str(tutorial_dir / path)
        for path in sorted(os.listdir(tutorial_dir))
    ]