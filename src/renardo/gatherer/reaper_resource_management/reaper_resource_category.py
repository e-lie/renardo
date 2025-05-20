from pathlib import Path
from typing import Dict, Optional, List, Iterator

from renardo.gatherer.reaper_resource_management.reaper_resource_file import ReaperResourceFile
from renardo.lib.music_resource import ResourceType


class ReaperResourceCategory:
    """Represents a collection of Reaper plugins/tracks in a category (e.g., 'bass', 'lead' or 'reverb', 'delay')."""
    def __init__(self, directory: Path, category: str, resource_type: ResourceType):
        self.directory = directory
        self.category = category
        self.type = resource_type
        self._reaper_resources: Dict[str, ReaperResourceFile] = {}
        self._load_resource_files()

    def _load_resource_files(self):
        """Load all Reaper resource files from the category directory."""
        valid_extensions = ['.py', '.rfxchain']
        
        for file_path in self.directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in [ext.lower() for ext in valid_extensions] and file_path.stem != '__init__':
                reaper_resource_file = ReaperResourceFile(file_path, self.type, self.category)
                self._reaper_resources[str(reaper_resource_file.name)] = reaper_resource_file


    def get_resource(self, name: str) -> Optional[ReaperResourceFile]:
        """Get a resource by its name."""
        return self._reaper_resources.get(name)

    def list_resources(self) -> List[str]:
        """List all resource names in this category."""
        return list(self._reaper_resources.keys())

    def __len__(self) -> int:
        return len(self._reaper_resources)

    def __iter__(self) -> Iterator[ReaperResourceFile]:
        return iter(self._reaper_resources.values())

    def __str__(self) -> str:
        return f"ReaperResourceCategory({self.type.value}/{self.category}, {len(self)} resources)"