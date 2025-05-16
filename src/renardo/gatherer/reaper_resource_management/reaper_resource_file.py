from enum import Enum
from pathlib import Path
from typing import Optional, Any
import importlib
import sys

from renardo.lib.music_resource import ResourceType

class ReaperResourceFile:
    """Represents a single Reaper track template/plugin file."""
    def __init__(self, path: Path, resource_type: ResourceType, category: str):
        self.path = path
        self.name = path.stem
        self.extension = path.suffix
        self.size = path.stat().st_size
        self.type = resource_type
        self.category = category

    @property
    def full_path(self) -> Path:
        return self.path

    def __str__(self) -> str:
        return f"ReaperResourceFile({self.type.value}/{self.category}/{self.name})"

    def __repr__(self) -> str:
        return self.__str__()

    def load_resource_from_python(self):
        """Load a resource defined in a Python file."""
        try:
            # Use importlib to load the Python module
            module_name = self.path.stem
            spec = importlib.util.spec_from_file_location(module_name, self.path)
            if spec is None or spec.loader is None:
                return None

            # Import here to avoid circular imports
            from renardo.reaper_backend.reaper_music_resource import ReaperInstrument, ReaperEffect
            from renardo.lib.music_resource import MusicResource, Instrument, Effect

            module = importlib.util.module_from_spec(spec)
            # Inject the necessary classes into the module namespace
            module.ReaperInstrument = ReaperInstrument
            module.ReaperEffect = ReaperEffect
            # Also provide the base classes in case they're needed
            module.MusicResource = MusicResource
            module.Instrument = Instrument
            module.Effect = Effect
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Look for the resource
            if hasattr(module, module_name):
                resource = getattr(module, module_name)
                # Set the resource name from the file
                if hasattr(resource, 'name') and not resource.name:
                    resource.name = self.name
                    resource.category = self.category
                return resource
            else:
                # If the resource is not named after the module, try to find it
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, MusicResource):
                        if hasattr(attr, 'name') and not attr.name:
                            attr.name = self.name
                            attr.category = self.category
                        return attr
            
            return None
        except FileNotFoundError:
            print(f"Resource file not found: {self.path}")
            return None
        except Exception as e:
            print(f"Error loading resource from {self.path}: {e}")
            return None