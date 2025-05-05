
from pathlib import Path
from .settings_manager import settings

recording_dir = settings.get_path("RECORDING_DIR")
recording_dir.mkdir(exist_ok=True, parents=True)

settings.set_defaults_from_dict({
    "sc_backend": {
        "ACTIVATED_SCCODE_BANKS": ['foxdot_core', 'foxdot_community', 'crashserver'],
        "OSC_MIDI_ADDRESS": "/foxdot_midi",
        "GET_SC_INFO": True,
        "ADDRESS": 'localhost',
        "PORT": 57110,
        "PORT2": 57120,
        "FORWARD_PORT": 0,
        "FORWARD_ADDRESS": '',
        "BOOT_SCLANG_ON_STARTUP": False,
        "SC3_PLUGINS": False,
    }
},
)

settings.set_defaults_from_dict({
    "sc_backend": {
        "INFO_FILE": "Info.scd",
        "RECORD_FILE" : "Record.scd",
        "STARTUP_FILE" : "Startup.scd",
        "OSC_FUNC_FILE" : "OSCFunc.scd",
        "BUFFERS_FILE" : "Buffers.scd",
        "EFFECTS_FILE": "Effects.scd",
        "SUPERCOLLIDER": "",
        "SCCODE_LIBRARY_DIR_NAME": "sccode_library",
        "SPECIAL_SCCODE_DIR_NAME": "special_sccode",
        "DEFAULT_SCCODE_PACK_NAME": "0_foxdot_core",
    }
},
internal=True
)

settings.save_to_file()