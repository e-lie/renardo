from pathlib import Path
from typing import Dict, Optional, List, Iterator, Any
import importlib.util
import sys

from renardo.gatherer.sccode_management.sccode_type_and_file import SCCodeType
from renardo.gatherer.sccode_management.sc_resource import SCSynth, SCEffect


class SCCodeCategory:
    """Represents a collection of resources (synths or effects) in a category (e.g., 'bass', 'lead' or 'reverb', 'delay')."""
    def __init__(self, directory: Path, category: str, synth_type: SCCodeType, default_arguments: Dict[str, Any] = None):
        self.directory = directory
        self.category = category
        self.type = synth_type
        self.default_arguments = default_arguments or {}
        self._resources = {}
        self._load_resources()

    def _load_resources(self):
        """Load all resource files from the category directory."""
        if not self.directory.exists():
            return
            
        for file_path in self.directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() == '.py' and file_path.stem != '__init__':
                try:
                    resource = self._load_resource_from_python(file_path)
                    if resource:
                        # Set the category if not already set
                        if hasattr(resource, 'category') and not resource.category:
                            resource.category = self.category
                        self._resources[resource.shortname] = resource
                except Exception as e:
                    print(f"Error loading resource {file_path}: {e}")

    def _load_resource_from_python(self, file_path: Path):
        """Load a resource defined in a Python file."""
        try:
            # Use importlib to load the Python module
            module_name = file_path.stem
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                return None
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Look for a resource instance in the module
            resource = None
            if self.type == SCCodeType.INSTRUMENT and hasattr(module, 'synth'):
                resource = module.synth
            elif self.type == SCCodeType.EFFECT and hasattr(module, 'effect'):
                resource = module.effect
                
            # Apply default arguments if they don't exist in the resource
            if resource and hasattr(resource, 'arguments'):
                for arg_name, default_value in self.default_arguments.items():
                    if arg_name not in resource.arguments:
                        resource.arguments[arg_name] = default_value
                        
            return resource
        except Exception as e:
            print(f"Error importing {file_path}: {e}")
            return None

    def get_resource(self, name: str):
        """Get a resource by its name."""
        return self._resources.get(name)

    def list_resources(self) -> List[str]:
        """List all resource names in this category."""
        return list(self._resources.keys())
        
    def get_resource_details(self) -> List[Dict[str, Any]]:
        """
        Get detailed information about all resources in this category.
        Returns a list of dictionaries containing shortname, fullname, and description.
        """
        return [
            {
                "shortname": resource.shortname,
                "fullname": resource.fullname,
                "description": resource.description,
                "arguments": list(resource.arguments.keys())
            }
            for resource in self._resources.values()
        ]

    def __len__(self) -> int:
        return len(self._resources)

    def __iter__(self) -> Iterator:
        return iter(self._resources.values())

    def __str__(self) -> str:
        return f"SCCodeCategory({self.type.value}/{self.category}, {len(self)} resources)"