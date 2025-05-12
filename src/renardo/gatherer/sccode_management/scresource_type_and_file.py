from enum import Enum
from pathlib import Path
from typing import Optional, Any
import importlib
import sys

from renardo.lib.music_resource import ResourceType

class SCResourceFile:
    """Represents a single SuperCollider synthdef file."""
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
        return f"SCResourceFile({self.type.value}/{self.category}/{self.name})"

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
            from renardo.sc_backend.sc_music_resource import SCInstrument, SCEffect
            from renardo.lib.music_resource import MusicResource, Instrument, Effect

            module = importlib.util.module_from_spec(spec)
            # Inject the necessary classes into the module namespace
            module.SCInstrument = SCInstrument
            module.SCEffect = SCEffect
            # Also provide the base classes in case they're needed
            module.MusicResource = MusicResource
            module.Instrument = Instrument
            module.Effect = Effect
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Look for a resource instance in the module
            resource = None
            if self.type == ResourceType.INSTRUMENT and hasattr(module, 'synth'):
                resource = module.synth
            elif self.type == ResourceType.EFFECT and hasattr(module, 'effect'):
                resource = module.effect

            # Apply default arguments if they don't exist in the resource
            # TODO fixxxx
            # if resource and hasattr(resource, 'arguments'):
            #     for arg_name, default_value in self.default_arguments.items():
            #         if arg_name not in resource.arguments:
            #             resource.arguments[arg_name] = default_value

            return resource
        except Exception as e:
            print(f"Error importing {self.path}: {e}")
            return None