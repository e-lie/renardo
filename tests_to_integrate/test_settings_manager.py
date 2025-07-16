import pytest
from pathlib import Path
import tomli
import os
from renardo.sc_backend.settings_manager import SettingsManager


@pytest.fixture
def public_defaults():
    """Fixture providing default public settings."""
    return {
        "app": {
            "name": "TestApp",
            "version": "1.0.0",
            "window": {
                "width": 800,
                "height": 600
            }
        }
    }


@pytest.fixture
def internal_defaults():
    """Fixture providing default internal settings."""
    return {
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


@pytest.fixture
def temp_files(tmp_path):
    """Fixture providing temporary file paths."""
    return {
        "public": tmp_path / "settings.toml",
        "internal": tmp_path / "internal.toml"
    }


@pytest.fixture
def settings_manager(temp_files, public_defaults, internal_defaults):
    """Fixture providing a SettingsManager instance."""
    return SettingsManager(
        temp_files["public"],
        temp_files["internal"],
        public_defaults,
        internal_defaults
    )


class TestSettingsManager:
    def test_initialization(self, settings_manager, public_defaults, internal_defaults):
        """Test if SettingsManager initializes with default settings."""
        # Check public settings
        assert settings_manager.get("app.name") == public_defaults["app"]["name"]
        assert settings_manager.get("app.window.width") == public_defaults["app"]["window"]["width"]

        # Check internal settings
        assert settings_manager.get("server.host", internal=True) == internal_defaults["server"]["host"]
        assert settings_manager.get("server.port", internal=True) == internal_defaults["server"]["port"]

    def test_save_and_load_public(self, settings_manager, temp_files):
        """Test if public settings are correctly saved and loaded."""
        # Modify public settings
        settings_manager.set("app.name", "NewName")
        settings_manager.set("app.window.width", 1024)

        # Save only public settings
        assert settings_manager.save(save_internal=False)
        assert temp_files["public"].exists()
        assert not temp_files["internal"].exists()

        # Create new instance and verify
        new_manager = SettingsManager(
            temp_files["public"],
            temp_files["internal"],
            settings_manager._public_defaults,
            settings_manager._internal_defaults
        )

        assert new_manager.get("app.name") == "NewName"
        assert new_manager.get("app.window.width") == 1024

    def test_save_and_load_internal(self, settings_manager, temp_files):
        """Test if internal settings are correctly saved and loaded."""
        # Modify internal settings
        settings_manager.set("user.api_key", "secret", internal=True)
        settings_manager.set("server.port", 9000, internal=True)

        # Save both public and internal
        assert settings_manager.save()
        assert temp_files["public"].exists()
        assert temp_files["internal"].exists()

        # Create new instance and verify
        new_manager = SettingsManager(
            temp_files["public"],
            temp_files["internal"],
            settings_manager._public_defaults,
            settings_manager._internal_defaults
        )

        assert new_manager.get("user.api_key", internal=True) == "secret"
        assert new_manager.get("server.port", internal=True) == 9000

    def test_reset_specific_public(self, settings_manager, public_defaults):
        """Test resetting specific public settings."""
        # Change settings
        settings_manager.set("app.name", "NewName")
        settings_manager.set("app.window.width", 1024)

        # Reset only app.name
        settings_manager.reset("app.name")

        # Verify reset and unchanged settings
        assert settings_manager.get("app.name") == public_defaults["app"]["name"]
        assert settings_manager.get("app.window.width") == 1024

    def test_reset_specific_internal(self, settings_manager, internal_defaults):
        """Test resetting specific internal settings."""
        # Change settings
        settings_manager.set("user.api_key", "secret", internal=True)
        settings_manager.set("server.port", 9000, internal=True)

        # Reset only server.port
        settings_manager.reset("server.port", internal=True)

        # Verify reset and unchanged settings
        assert settings_manager.get("user.api_key", internal=True) == "secret"
        assert settings_manager.get("server.port", internal=True) == internal_defaults["server"]["port"]

    def test_reset_all(self, settings_manager, public_defaults, internal_defaults):
        """Test resetting all settings."""
        # Change multiple settings
        settings_manager.set("app.name", "NewName")
        settings_manager.set("user.api_key", "secret", internal=True)

        # Reset all public settings
        settings_manager.reset()

        # Reset all internal settings
        settings_manager.reset(internal=True)

        # Verify all settings are back to defaults
        assert settings_manager.get("app.name") == public_defaults["app"]["name"]
        assert settings_manager.get("user.api_key", internal=True) == internal_defaults["user"]["api_key"]

    def test_invalid_files(self, tmp_path, public_defaults, internal_defaults):
        """Test handling of invalid settings files."""
        # Create invalid TOML files
        invalid_public = tmp_path / "invalid_public.toml"
        invalid_internal = tmp_path / "invalid_internal.toml"

        invalid_public.write_text("invalid:toml:[content")
        invalid_internal.write_text("more:invalid:content")

        # Should not raise exception and use defaults
        manager = SettingsManager(
            invalid_public,
            invalid_internal,
            public_defaults,
            internal_defaults
        )

        assert manager.get("app.name") == public_defaults["app"]["name"]
        assert manager.get("server.port", internal=True) == internal_defaults["server"]["port"]

    def test_nonexistent_directories(self, tmp_path, public_defaults, internal_defaults):
        """Test saving to files in non-existent directories."""
        deep_public = tmp_path / "deep" / "path" / "settings.toml"
        deep_internal = tmp_path / "deep" / "path" / "internal.toml"

        manager = SettingsManager(deep_public, deep_internal, public_defaults, internal_defaults)

        # Should create directories and save successfully
        assert manager.save()
        assert deep_public.exists()
        assert deep_internal.exists()

    def test_type_preservation(self, settings_manager):
        """Test if types are preserved when saving and loading."""
        test_values = {
            "string": "test",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"key": "value"}
        }

        # Set test values in both public and internal settings
        for key, value in test_values.items():
            settings_manager.set(f"types.{key}", value)
            settings_manager.set(f"types.{key}", value, internal=True)

        # Save and create new instance
        settings_manager.save()
        new_manager = SettingsManager(
            settings_manager.public_file,
            settings_manager.internal_file,
            settings_manager._public_defaults,
            settings_manager._internal_defaults
        )

        # Verify types in both public and internal settings
        for key, value in test_values.items():
            # Check public settings
            loaded_value = new_manager.get(f"types.{key}")
            assert isinstance(loaded_value, type(value))
            assert loaded_value == value

            # Check internal settings
            loaded_value = new_manager.get(f"types.{key}", internal=True)
            assert isinstance(loaded_value, type(value))
            assert loaded_value == value

    def test_file_permissions(self, settings_manager, temp_files):
        """Test handling of permission errors."""
        if os.name != 'nt':  # Skip on Windows
            # Save initially
            settings_manager.save()

            # Make files readonly
            temp_files["public"].chmod(0o444)
            temp_files["internal"].chmod(0o444)

            # Attempt to save to readonly files
            assert settings_manager.save() == False

    def test_concurrent_access(self, temp_files, public_defaults, internal_defaults):
        """Test if multiple SettingsManager instances can access the same files."""
        manager1 = SettingsManager(
            temp_files["public"],
            temp_files["internal"],
            public_defaults,
            internal_defaults
        )
        manager2 = SettingsManager(
            temp_files["public"],
            temp_files["internal"],
            public_defaults,
            internal_defaults
        )

        # Modify settings in first instance
        manager1.set("app.name", "Manager1")
        manager1.set("server.port", 9000, internal=True)
        manager1.save()

        # Load in second instance
        manager2.load()
        assert manager2.get("app.name") == "Manager1"
        assert manager2.get("server.port", internal=True) == 9000