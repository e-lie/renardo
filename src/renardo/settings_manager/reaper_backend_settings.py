from .settings_manager import settings

settings.set_defaults_from_dict({
    "reaper_backend": {
        "REAPER_BACKEND_ENABLED": True,
        "ACTIVATED_REAPER_BANKS": [
            "renardo_core"
        ],
        "SELECTED_REAPER_INSTRUMENTS": [
            "bass303",
            "lonesine"
        ]
    }
},
)

settings.set_defaults_from_dict({
    "reaper_backend": {
        "REAPER_LIBRARY_DIR_NAME": "reaper_library",
        "DEFAULT_REAPER_PACK_NAME": "0_renardo_core",
    }
},
internal=True
)

settings.save_to_file()