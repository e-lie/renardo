from pathlib import Path
import tomli
import tomli_w
from typing import Any, Dict, Optional
import copy
import os
import pathlib
from sys import platform


class SettingsManager:
    """Manages application settings with separate public and internal TOML files."""

    def __init__(
            self,
            public_file: Path,
            internal_file: Path,
            public_defaults: Dict[str, Any],
            internal_defaults: Dict[str, Any]
    ):
        """
        Initialize settings manager.

        Args:
            public_file: Path to public settings TOML file
            internal_file: Path to internal settings TOML file
            public_defaults: Dictionary of default public settings
            internal_defaults: Dictionary of default internal settings
        """
        self.public_file = Path(public_file)
        self.internal_file = Path(internal_file)

        self._public_defaults = copy.deepcopy(public_defaults)
        self._internal_defaults = copy.deepcopy(internal_defaults)

        self._public_settings = copy.deepcopy(public_defaults)
        self._internal_settings = copy.deepcopy(internal_defaults)

        # Load both settings files
        self.load_from_file()

    def load_from_file(self) -> None:
        """Load settings from both public and internal TOML files."""
        # Load public settings
        try:
            if self.public_file.exists():
                with open(self.public_file, "rb") as f:
                    loaded_settings = tomli.load(f)
                self._recursive_update(self._public_settings, loaded_settings)
        except Exception as e:
            print(f"Error loading public settings: {e}")

        # Load internal settings
        try:
            if self.internal_file.exists():
                with open(self.internal_file, "rb") as f:
                    loaded_settings = tomli.load(f)
                self._recursive_update(self._internal_settings, loaded_settings)
        except Exception as e:
            print(f"Error loading internal settings: {e}")

    def save_to_file(self, save_internal: bool = True) -> bool:
        """
        Save current settings to TOML files.

        Args:
            save_internal: Whether to save internal settings

        Returns:
            True if all requested saves were successful
        """
        success = True

        # Save public settings
        try:
            self.public_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.public_file, "wb") as f:
                tomli_w.dump(self._public_settings, f)
        except Exception as e:
            print(f"Error saving public settings: {e}")
            success = False

        # Save internal settings if requested
        if save_internal:
            try:
                self.internal_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.internal_file, "wb") as f:
                    tomli_w.dump(self._internal_settings, f)
            except Exception as e:
                print(f"Error saving internal settings: {e}")
                success = False

        return success

    def set_from_dict(self, settings_dict: Dict[str, Any], internal: bool = False) -> None:
        """
        Add multiple settings at once from a dictionary.

        Args:
            settings_dict: Dictionary of settings to add
            internal: Whether to add to internal settings
        """
        target = self._internal_settings if internal else self._public_settings
        self._recursive_update(target, settings_dict)

    def set_defaults_from_dict(self, defaults_dict: Dict[str, Any], internal: bool = False) -> None:
        """
        Set defaults from a dictionary and add them to settings only if keys don't already exist.

        Args:
            defaults_dict: Dictionary of default settings to add
            internal: Whether to set defaults for internal settings
        """
        # First update the defaults
        defaults = self._internal_defaults if internal else self._public_defaults
        self._recursive_update(defaults, defaults_dict)

        # Then add to settings only if keys don't exist
        settings = self._internal_settings if internal else self._public_settings
        self._recursive_update_if_not_exists(settings, defaults_dict)

    def _recursive_update_if_not_exists(self, target: Dict, source: Dict) -> None:
        """Recursively update nested dictionaries, but only for keys that don't exist in target."""
        for key, value in source.items():
            if key not in target:
                # Key doesn't exist, add it
                target[key] = copy.deepcopy(value)
            elif isinstance(target[key], dict) and isinstance(value, dict):
                # Key exists and both are dictionaries, recurse
                self._recursive_update_if_not_exists(target[key], value)
            # If key exists but is not a dict, keep the existing value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.

        Args:
            key: Setting key (supports dot notation)
            default: Value to return if key doesn't exist
            internal: Whether to get from internal settings

        Returns:
            Setting value or default if not found
        """

        try:
            value = self._internal_settings
            for k in key.split('.'):
                value = value[k]
            return value
        except KeyError: # if not in internal settings try with public settings
            try:
                value = self._public_settings
                for k in key.split('.'):
                    value = value[k]
                return value
            except KeyError:
                return default

    def set(self, key: str, value: Any, internal: bool = False) -> None:
        """
        Set a setting value.

        Args:
            key: Setting key (supports dot notation)
            value: Value to set
            internal: Whether to set in internal settings
        """
        settings = self._internal_settings if internal else self._public_settings

        keys = key.split('.')
        current = settings

        # Navigate to the deepest dict
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        # Set the value
        current[keys[-1]] = value

    def reset(self, key: Optional[str] = None, internal: bool = False) -> None:
        """
        Reset settings to defaults.

        Args:
            key: Specific key to reset, or None to reset all
            internal: Whether to reset internal settings
        """
        settings = self._internal_settings if internal else self._public_settings
        defaults = self._internal_defaults if internal else self._public_defaults

        if key is None:
            if internal:
                self._internal_settings = copy.deepcopy(self._internal_defaults)
            else:
                self._public_settings = copy.deepcopy(self._public_defaults)
        else:
            try:
                value = defaults
                for k in key.split('.'):
                    value = value[k]
                self.set(key, copy.deepcopy(value), internal)
            except KeyError:
                pass

    def _recursive_update(self, target: Dict, source: Dict) -> None:
        """Recursively update nested dictionaries."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._recursive_update(target[key], value)
            else:
                target[key] = value

RENARDO_USER_DIR : Optional[Path] = None

# default config path
# on windows AppData/Roaming/renardo
# on Linux ~/.config/renardo
# on MacOS /Users/<username>/Library/Application Support/renardo
if platform == "linux" or platform == "linux2" :
    home_path = pathlib.Path.home()
    RENARDO_USER_DIR = home_path / '.config' / 'renardo'
elif platform == "darwin":
    home_path = pathlib.Path.home()
    RENARDO_USER_DIR = home_path / 'Library' / 'Application Support' / 'renardo'
elif platform == "win32":
    appdata_roaming_path = pathlib.Path(os.getenv('APPDATA'))
    RENARDO_USER_DIR = appdata_roaming_path / 'renardo'

# def get_user_config_dir_path():
#     return RENARDO_USER_DIR

public_defaults = {
    "core": {
        "RENARDO_USER_DIR": str(RENARDO_USER_DIR),
        "PUBLIC_SETTINGS_FILE": str(RENARDO_USER_DIR / "settings.toml")
    }
}

internal_defaults = {
    "samples": {
        "SAMPLES_DIR": str(RENARDO_USER_DIR / 'sample_packs')
    },
    "core": {
        "INTERNAL_SETTINGS_FILE": str(RENARDO_USER_DIR / "internal_settings.toml")
    }
}

settings = SettingsManager(
    Path(RENARDO_USER_DIR/"settings.toml"),
    Path(RENARDO_USER_DIR/"internal_settings.toml"),
    public_defaults,
    internal_defaults
)

settings.save_to_file()