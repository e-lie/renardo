from pathlib import Path
from typing import Dict, Iterator, List, Optional

from renardo.gatherer.reaper_resource_management.reaper_resource_category import ReaperResourceCategory
from renardo.gatherer.reaper_resource_management.reaper_resource_file import ReaperResourceFile
from renardo.lib.music_resource import ResourceType


class ReaperResourceSection:
    """Represents a section of categories for either instruments or effects."""
    def __init__(self, directory: Path, resource_type: ResourceType):
        self.directory = directory
        self.type = resource_type
        self._categories: Dict[str, ReaperResourceCategory] = {}
        self._load_categories()

    def _load_categories(self):
        """Load all categories from the section directory."""
        if not self.directory.exists():
            return
        for category_dir in self.directory.iterdir():
            if category_dir.is_dir():
                category_name = category_dir.name
                category = ReaperResourceCategory(category_dir, category_name, self.type)
                self._categories[category_name] = category

    def get_category(self, category_name: str) -> Optional[ReaperResourceCategory]:
        """Get a category by its name."""
        return self._categories.get(category_name)

    def list_categories(self) -> List[str]:
        """List all category names."""
        return list(self._categories.keys())

    def __len__(self) -> int:
        return len(self._categories)

    def __iter__(self) -> Iterator[ReaperResourceCategory]:
        return iter(self._categories.values())

    def get_resource(self, category: str, resource_name: str) -> Optional[ReaperResourceFile]:
        """Get a specific resource from a category."""
        category_obj = self.get_category(category)
        if category_obj:
            return category_obj.get_resource(resource_name)
        return None