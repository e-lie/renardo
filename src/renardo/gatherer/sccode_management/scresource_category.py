from pathlib import Path
from typing import Dict, Optional, List, Iterator

from renardo.gatherer.sccode_management.scresource_type_and_file import SCResourceFile
from renardo.lib.music_resource import ResourceType


class SCResourceCategory:
    """Represents a collection of synthdefs in a category (e.g., 'bass', 'lead' or 'reverb', 'delay')."""
    def __init__(self, directory: Path, category: str, resource_type: ResourceType):
        self.directory = directory
        self.category = category
        self.type = resource_type
        self._sc_resources: Dict[str, SCResourceFile] = {}
        self._load_resource_files()

    def _load_resource_files(self):
        """Load all supercollider python resource files from the category directory."""
        for file_path in self.directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() == '.py' and file_path.stem != '__init__':
                sc_resource_file = SCResourceFile(file_path, self.type, self.category)
                self._sc_resources[str(sc_resource_file.name)] = sc_resource_file


    def get_resource(self, name: str) -> Optional[SCResourceFile]:
        """Get a synthdef by its name."""
        return self._sc_resources.get(name)

    def list_resources(self) -> List[str]:
        """List all synthdef names in this category."""
        return list(self._sc_resources.keys())

    def __len__(self) -> int:
        return len(self._sc_resources)

    def __iter__(self) -> Iterator[SCResourceFile]:
        return iter(self._sc_resources.values())

    def __str__(self) -> str:
        return f"SCCodeCategory({self.type.value}/{self.category}, {len(self)} synthdefs)"
