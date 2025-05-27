"""
Webclient settings module for Renardo.

This module defines settings related to the web-based code editor
and user interface preferences for the webclient.
"""
from .settings_manager import settings

# Define default public settings
webclient_public_defaults = {
    "webclient": {
        "EDITOR_COLOR_SCHEME": "monokai",  # Default CodeMirror theme
        "FONT_SIZE": 14,                   # Default editor font size
        "LINE_NUMBERS": True,              # Show line numbers by default
        "WORD_WRAP": False,                # Disable word wrap by default
        "AUTO_SAVE": True,                 # Auto-save code changes
        "THEME": "dark",                   # Overall UI theme (dark/light)
    }
}

# Define default internal settings (not visible/changeable by users)
webclient_internal_defaults = {
    "webclient": {
        "AVAILABLE_THEMES": [
            "darcula", "dracula", "eclipse", "material", 
            "monokai", "nord", "solarized-dark", "solarized-light"
        ],  # Available CodeMirror themes
        "SESSION_TIMEOUT": 3600,           # Session timeout in seconds
        "MAX_CODE_LENGTH": 50000,          # Maximum code length in characters
    }
}

# Register the defaults with the settings manager
settings.set_defaults_from_dict(webclient_public_defaults)
settings.set_defaults_from_dict(webclient_internal_defaults, internal=True)

# Save the settings
settings.save_to_file()