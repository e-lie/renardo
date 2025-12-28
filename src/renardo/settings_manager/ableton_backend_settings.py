from .settings_manager import settings

settings.set_defaults_from_dict({
    "ableton_backend": {
        "ABLETON_BACKEND_ENABLED": False,
        "ABLETON_MAX_MIDI_TRACKS": 16,
        "ABLETON_SCAN_AUDIO_TRACKS": True,
        "ABLETON_AUTO_SCAN": False,
    }
},
)

settings.save_to_file()
