import re
from pathlib import Path
from typing import Dict, Optional, List, Iterator

from .sample_category import SampleCategory
from .sample_file import SampleFile


class SamplePack:
    """Represents a collection of categorized samples in a directory."""
    def __init__(self, directory: Path):
        self.directory = directory
        self._categories: Dict[str, SampleCategory] = {}
        self.name = self._parse_pack_name(directory.name)
        self.index = self._parse_pack_index(directory.name)
        self._load_categories()

    @staticmethod
    def _parse_pack_name(dirname: str) -> str:
        """Extract pack name from directory name format: {index}_{name}."""
        match = re.match(r'\d+_(.+)', dirname)
        if not match:
            raise ValueError(f"Invalid pack directory format: {dirname}")
        return match.group(1)

    @staticmethod
    def _parse_pack_index(dirname: str) -> int:
        """Extract pack index from directory name format: {index}_{name}."""
        match = re.match(r'(\d+)_', dirname)
        if not match:
            raise ValueError(f"Invalid pack directory format: {dirname}")
        return int(match.group(1))

    def _load_categories(self):
        """Load all category folders and their samples."""
        for category_dir in self.directory.iterdir():
            if category_dir.is_dir():
                category = category_dir.name  # The letter/symbol
                self._categories[category] = SampleCategory(category_dir, category)

    def get_category(self, category: str) -> Optional[SampleCategory]:
        """Get a category by its letter/symbol."""
        return self._categories.get(category)

    def get_sample(self, category: str, index: int) -> Optional[SampleFile]:
        """Get a sample by its category and index."""
        category_obj = self.get_category(category)
        if category_obj:
            return category_obj.get_sample(index)
        return None

    def list_categories(self) -> List[str]:
        """List all category letters/symbols."""
        return list(self._categories.keys())

    def __len__(self) -> int:
        return len(self._categories)

    def __iter__(self) -> Iterator[SampleCategory]:
        return iter(self._categories.values())

    def __str__(self) -> str:
        return f"SamplePack({self.index}: {self.name}, {len(self)} categories)"
