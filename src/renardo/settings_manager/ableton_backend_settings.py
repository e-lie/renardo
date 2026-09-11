from .settings_manager import settings

settings.set_defaults_from_dict({
    "ableton_backend": {
        "ABLETON_BACKEND_ENABLED": False,
        "ABLETON_SYNC_SCALE_ROOT": True,
    }
},
)

settings.save_to_file()
