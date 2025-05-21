
from .settings_manager import settings

recording_dir = settings.get_path("RECORDING_DIR")
recording_dir.mkdir(exist_ok=True, parents=True)

settings.set_defaults_from_dict({
    "sc_backend": {
        # Select the Supercollider instruments and effects bank that should be loaded
        "ACTIVATED_SCCODE_BANKS": ['foxdot_core', 'foxdot_community', 'crashserver'],
        # Indicate to which ouput device should the Renardo supercollider midi connect by default
        # You can list the midi device in the corresponding section of Audio backends > SuperCollider > MIDI.
        # "SUPERCOLLIDER_MIDI_OUTPUT_NUMBER": 0,
    }
},
)

settings.set_defaults_from_dict({
    "sc_backend": {
        "OSC_MIDI_ADDRESS": "/foxdot_midi",
        "GET_SC_INFO": True,
        "ADDRESS": 'localhost',
        "PORT": 57110,
        "PORT2": 57120,
        "FORWARD_PORT": 0,
        "FORWARD_ADDRESS": '',
        "BOOT_SCLANG_ON_STARTUP": False,
        "SC3_PLUGINS": False,
        "INFO_FILE": "Info.scd",
        "RECORD_FILE" : "Record.scd",
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