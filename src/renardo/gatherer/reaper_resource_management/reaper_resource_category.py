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
        # Dictionary to track Python and RfxChain files by stem name
        resources_by_stem = {}
        
        # First pass - collect all files by their stem name
        for file_path in self.directory.iterdir():
            if file_path.is_file() and file_path.stem != '__init__':
                stem = file_path.stem
                ext = file_path.suffix.lower()
                
                if stem not in resources_by_stem:
                    resources_by_stem[stem] = {'py': None, 'rfxchain': None}
                
                if ext.lower() == '.py':
                    resources_by_stem[stem]['py'] = file_path
                elif ext.lower() == '.rfxchain':
                    resources_by_stem[stem]['rfxchain'] = file_path
        
        # Second pass - create resource files, prefer Python files over RfxChain files
        for stem, files in resources_by_stem.items():
            # Python files contain the actual resource definition
            if files['py']:
                reaper_resource_file = ReaperResourceFile(files['py'], self.type, self.category)
                self._reaper_resources[stem] = reaper_resource_file
            # If no Python file but there's an RfxChain file, use that
            elif files['rfxchain']:
                reaper_resource_file = ReaperResourceFile(files['rfxchain'], self.type, self.category)
                self._reaper_resources[stem] = reaper_resource_file
                
        print(f"Loaded {len(self._reaper_resources)} resources in category {self.category}")


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