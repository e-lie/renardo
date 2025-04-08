
from pathlib import Path
from .settings_manager import settings

SCLANG_DIR_PATH = Path(settings.get("core.RENARDO_USER_DIR")) / 'sclang_code'
RECORDING_DIR = Path(settings.get("core.RENARDO_USER_DIR")) / "rec"
RECORDING_DIR.mkdir(exist_ok=True)

# def GET_SYNTHDEF_FILES():
#    return [os.path.realpath(settings.get("sc_backend.SYNTHDEF_DIR") + "/" + path) for path in os.listdir(settings.get("sc_backend.SYNTHDEF_DIR"))]

# def GET_FX_FILES():
#    return [os.path.realpath(settings.get("sc_backend.EFFECTS_DIR") + "/" + path) for path in os.listdir(settings.get("sc_backend.EFFECTS_DIR"))]

settings.set_defaults_from_dict({
    "sc_backend": {
        "SCCODE_LIBRARY": str(Path(settings.get("core.RENARDO_USER_DIR")) / 'sccode_library'),
        "SPECIAL_SCCODE_DIR": str(Path(settings.get("core.RENARDO_USER_DIR")) / "special_sccode"),
        "ACTIVATED_SCCODE_BANKS": ['foxdot_core', 'foxdot_community', 'crashserver'],
        "RECORDING_DIR": str(RECORDING_DIR),
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
        "SCLANG_CODE_DIR_PATH": str(SCLANG_DIR_PATH),
        "INFO_FILE": str(SCLANG_DIR_PATH / "Info.scd"),
        "RECORD_FILE" : str(SCLANG_DIR_PATH / "Record.scd"),
        "STARTUP_FILE" : str(SCLANG_DIR_PATH / "Startup.scd"),
        "OSC_FUNC_FILE" : str(SCLANG_DIR_PATH / "OSCFunc.scd"),
        "BUFFERS_FILE" : str(SCLANG_DIR_PATH / "Buffers.scd"),
        "EFFECTS_FILE": str(SCLANG_DIR_PATH / "Effects.scd"),
        # Directory for permanent/externally managed .scd file for synths
        # (not overwritten)
        "SYNTHDEF_DIR" : str(SCLANG_DIR_PATH / "scsynth"),
        "EFFECTS_DIR": str(SCLANG_DIR_PATH / "sceffects"),
        "ENVELOPE_DIR": str(SCLANG_DIR_PATH / "scenvelopes"),
        # Directory to write temporary Python generated or Live sclang .scd synths
        # To avoid overwriting permanent (default) synthdef scd files
        "TMP_SYNTHDEF_DIR" : str(SCLANG_DIR_PATH / "tmp_code" / "scsynth"),
        "TMP_EFFECTS_DIR": str(SCLANG_DIR_PATH / "tmp_code" / "sceffects"),
        "SUPERCOLLIDER": "",
    }
},
internal=True
)

settings.save_to_file()