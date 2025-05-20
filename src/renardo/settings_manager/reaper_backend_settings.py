from .settings_manager import settings

settings.set_defaults_from_dict({
    "reaper_backend": {
        "REAPER_BACKEND_ENABLED": False,
        "ACTIVATED_REAPER_BANKS": [
            "renardo_core"
        ]
    }
},
)

settings.set_defaults_from_dict({
    "reaper_backend": {
        "REAPER_LIBRARY_DIR_NAME": "reaper_library",
    }
},
internal=True
)

settings.save_to_file()