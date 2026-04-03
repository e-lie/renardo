from .settings_manager import settings

settings.set_defaults_from_dict({
    "reaper_backend": {
        "REAPER_BACKEND_ENABLED": True,
    }
},
)

settings.save_to_file()