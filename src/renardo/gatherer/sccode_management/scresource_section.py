from pathlib import Path
from typing import Dict, Optional, List, Iterator

from renardo.lib.music_resource import ResourceType
from renardo.gatherer.sccode_management.scresource_category import SCResourceCategory


class SCResourceSection:
    """Represents either the instruments or effects section of a bank."""
    def __init__(self, directory: Path, resource_type: ResourceType):
        self.directory = directory
        self.type = resource_type
        self._categories: Dict[str, SCResourceCategory] = {}
        self._load_categories()

    def _load_categories(self):
        """Load all categories in this section."""
        if not self.directory.exists():
            return

        for category_dir in self.directory.iterdir():
            if category_dir.is_dir():
                category = category_dir.name
                self._categories[category] = SCResourceCategory(
                    category_dir,
                    category,
                    self.type
                )

    def get_category(self, category: str) -> Optional[SCResourceCategory]:
        """Get a category by its name."""
        return self._categories.get(category)

    def list_categories(self) -> List[str]:
        """List all category names."""
        return list(self._categories.keys())

    def __len__(self) -> int:
        return len(self._categories)

    def __iter__(self) -> Iterator[SCResourceCategory]:
        return iter(self._categories.values())

    def __str__(self) -> str:
        return f"SCResourceSection({self.type.value}, {len(self)} categories)"
