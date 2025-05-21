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

    def get(self, key: str, default: Any = None, internal=True) -> Any:
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
            value = self._public_settings
            for k in key.split('.'):
                value = value[k]
            return value
        except KeyError: # if not in public settings try with internal settings
            if internal:
                try:
                    value = self._internal_settings
                    for k in key.split('.'):
                        value = value[k]
                    return value
                except KeyError:
                    print(f"Setting {key} not found ! returning {default} ...")
                    return default
            else:
                print(f"Setting {key} not found ! returning {default} ...")
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

    @staticmethod
    def get_standard_config_dir():
        config_dir: Optional[Path] = None
        # standard config path
        # on windows AppData/Roaming/renardo
        # on Linux ~/.config/renardo
        # on MacOS /Users/<username>/Library/Application Support/renardo
        if platform == "linux" or platform == "linux2":
            home_path = pathlib.Path.home()
            config_dir = home_path / '.config'
        elif platform == "darwin":
            home_path = pathlib.Path.home()
            config_dir = home_path / 'Library' / 'Application Support'
        else: # platform == "win32":
            appdata_roaming_path = pathlib.Path(os.getenv('APPDATA'))
            config_dir = appdata_roaming_path
        return config_dir

    @staticmethod
    def get_standard_user_dir():
        return SettingsManager.get_standard_config_dir() / 'renardo'

    @staticmethod
    def set_user_dir_path(path: Path) -> bool:
        """
        Create or update user_dir.toml with a custom user directory path.
        
        Args:
            path: The path to set as the Renardo user directory
            
        Returns:
            True if successful, False otherwise
        """
        standard_dir = SettingsManager.get_standard_user_dir()
        user_dir_file = standard_dir / "user_dir.toml"
        
        try:
            standard_dir.mkdir(parents=True, exist_ok=True)
            config = {"RENARDO_USER_DIR_PATH": str(path)}
            
            with open(user_dir_file, "wb") as f:
                tomli_w.dump(config, f)
            return True
        except Exception as e:
            print(f"Error writing user_dir.toml: {e}")
            return False
    
    @staticmethod
    def get_renardo_user_dir():
        renardo_user_dir: Optional[Path] = None
        try: # if env variable exists to define custom user dir use it
            renardo_user_dir = Path(os.environ["RENARDO_USER_DIR"])
        except KeyError: # if not, check for user_dir.toml
            standard_dir = SettingsManager.get_standard_user_dir()
            user_dir_file = standard_dir / "user_dir.toml"
            
            if user_dir_file.exists():
                try:
                    with open(user_dir_file, "rb") as f:
                        user_dir_config = tomli.load(f)
                    if "RENARDO_USER_DIR_PATH" in user_dir_config:
                        renardo_user_dir = Path(user_dir_config["RENARDO_USER_DIR_PATH"])
                    else:
                        renardo_user_dir = standard_dir
                except Exception as e:
                    print(f"Error reading user_dir.toml: {e}")
                    renardo_user_dir = standard_dir
            else:
                # No user_dir.toml exists, use standard directory
                renardo_user_dir = standard_dir
        return renardo_user_dir

    def get_path(self, path_name: str) -> Optional[Path]:
        """Paths for files used by renardo and foxdot editor are dynamically resolved
        in one method depending on OS and initial user dir setting"""
        if path_name == "PUBLIC_SETTINGS_FILE":
            return self.get_renardo_user_dir() / "settings.toml"
        elif path_name == "INTERNAL_SETTINGS_FILE":
            return self.get_standard_user_dir() / "internal_settings.toml"
        elif path_name == "SAMPLES_DIR":
            return self.get_renardo_user_dir() / self.get("samples.SAMPLES_DIR_NAME")
        elif path_name == "RECORDING_DIR":
            return self.get_renardo_user_dir() / "rec"
        elif path_name == "STARTUP_FILES_DIR":
            return self.get_renardo_user_dir() / "startup_files"
        elif path_name == "SCCODE_LIBRARY":
            return self.get_renardo_user_dir() / self.get("sc_backend.SCCODE_LIBRARY_DIR_NAME")
        elif path_name == "SPECIAL_SCCODE_DIR":
            return self.get_renardo_user_dir() / self.get("sc_backend.SPECIAL_SCCODE_DIR_NAME")
        elif path_name == "LOOP_PATH":
            return self.get_path("SAMPLES_DIR") / self.get("samples.DEFAULT_SAMPLE_PACK_NAME") / self.get("samples.LOOP_DIR_NAME")
        # Directory for permanent/externally managed .scd file for synths
        # (not overwritten)
        # elif path_name == "SYNTHDEF_DIR":
        #     self.get_path("SCLANG_CODE_DIR_PATH") / "scsynth"
        # elif path_name == "EFFECTS_DIR":
        #     self.get_path("SCLANG_CODE_DIR_PATH") / "sceffects"
        # elif path_name == "ENVELOPE_DIR":
        #     self.get_path("SCLANG_CODE_DIR_PATH") / "scenvelopes"
        # Directory to write temporary Python generated or Live sclang .scd synths
        # To avoid overwriting permanent (default) synthdef scd files
        # elif path_name == "TMP_SYNTHDEF_DIR":
        #    return self.get_path("SCLANG_CODE_DIR_PATH") / "tmp_code" / "scsynth"
        # elif path_name == "TMP_EFFECTS_DIR":
        #     return self.get_path("SCLANG_CODE_DIR_PATH") / "tmp_code" / "sceffects"
        elif path_name == "REAPER_LIBRARY":
            return self.get_renardo_user_dir() / self.get("reaper_backend.REAPER_LIBRARY_DIR_NAME")
        elif path_name == "RENARDO_FXCHAIN_DIR":
            return self.get_standard_config_dir() / "REAPER" / "FXChains" / "renardo_fxchains"
        elif path_name == "RENARDO_ROOT_PATH":
            return Path(__file__).parent.parent
        elif path_name == "FOXDOT_EDITOR_ROOT":
            return self.get_path("RENARDO_ROOT_PATH") / "foxdot_editor"
        elif path_name == "STARTUP_FILE_PATH":
            startup_file_name = self.get("core.STARTUP_FILE_NAME", "default.py")
            return self.get_path("STARTUP_FILES_DIR") / startup_file_name

        else:
            raise KeyError(f"{path_name} does not exist")

public_defaults = {
    "core": {
    }
}

internal_defaults = {
    "samples": {
        "SAMPLES_DIR": str(SettingsManager.get_renardo_user_dir() / 'sample_packs')
    },
    "core": {
    }
}

settings = SettingsManager(
    SettingsManager.get_renardo_user_dir() / "settings.toml",
    SettingsManager.get_standard_user_dir() / "internal_settings.toml",
    public_defaults,
    internal_defaults
)

settings.save_to_file()