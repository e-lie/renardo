from pathlib import Path
import tomli
import tomli_w
from typing import Any, Dict, Optional
import copy


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
        self.load()

    def load(self) -> None:
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

    def save(self, save_internal: bool = True) -> bool:
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

    def get(self, key: str, default: Any = None, internal: bool = False) -> Any:
        """
        Get a setting value.

        Args:
            key: Setting key (supports dot notation)
            default: Value to return if key doesn't exist
            internal: Whether to get from internal settings

        Returns:
            Setting value or default if not found
        """
        settings = self._internal_settings if internal else self._public_settings

        try:
            value = settings
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


# Example usage
if __name__ == "__main__":
    # Define default settings
    public_defaults = {
        "app": {
            "name": "MyApp",
            "version": "1.0.0",
            "theme": "light",
            "window": {
                "width": 800,
                "height": 600
            }
        }
    }

    internal_defaults = {
        "user": {
            "api_key": "",
            "credentials": {
                "username": "",
                "password": ""
            }
        },
        "server": {
            "host": "localhost",
            "port": 8080
        }
    }

    # Create settings manager
    settings = SettingsManager(
        Path("settings.toml"),
        Path("internal.toml"),
        public_defaults,
        internal_defaults
    )

    # Work with public settings
    print(f"App name: {settings.get('app.name')}")
    settings.set('app.theme', 'dark')

    # Work with internal settings
    settings.set('user.api_key', 'secret_key', internal=True)
    print(f"API Key: {settings.get('user.api_key', internal=True)}")

    # Save both
    settings.save()

    # Save only public settings
    settings.save(save_internal=False)

    # Reset specific internal setting
    settings.reset('user.api_key', internal=True)

    # Reset all public settings
    settings.reset()