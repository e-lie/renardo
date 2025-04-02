import re
from pathlib import Path
from pprint import pformat
from typing import Dict, Optional, List, Iterator

from renardo.gatherer.sample_management.sample_category import SampleCategory
from renardo.settings_manager import settings
from renardo.gatherer.sample_management.sample_file import SampleFile

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
            # check if the folder is a single letter directory then use upper lower subdir
            # because macOS is not case-sensitive with file names WTF
            if  category_dir.is_dir() and len(category_dir.name)==1 and category_dir.name in settings.get("samples.ALPHA")+settings.get("samples.ALPHA").upper():

                lower_category = category_dir.name.lower()
                upper_category = category_dir.name.upper()
                self._categories[lower_category] = SampleCategory(category_dir / 'lower', lower_category)
                self._categories[upper_category] = SampleCategory(category_dir / 'upper', upper_category)
            elif category_dir.is_dir():
                category = category_dir.name  # The letter/symbol
                self._categories[category] = SampleCategory(category_dir, category)

    def get_category(self, category: str) -> Optional[SampleCategory]:
        """Get a category by its letter/symbol."""
        category_fullname = settings.get("samples.NON_ALPHA")[category] if category in settings.get("samples.NON_ALPHA").keys() else category
        return self._categories.get(category_fullname)

    def get_sample(self, category: str, index: int) -> Optional[SampleFile]:
        """Get a sample by its category and index."""
        category_obj = self.get_category(category)
        if category_obj:
            return category_obj.get_sample(index)
        return None

    def list_categories(self) -> List[str]:
        """List all category letters/symbols."""
        return list(self._categories.keys())

    def sample_count(self) -> int:
        """Returns total number of samples across all categories."""
        return sum(len(category) for category in self._categories.values())

    def __len__(self) -> int:
        return len(self._categories)

    def __iter__(self) -> Iterator[SampleCategory]:
        return iter(self._categories.values())

    def __repr__(self) -> str:
        return f"<SamplePack {self.name}>"

    def __str__(self) -> str:
        return f"Sample pack {self.index}: {self.name}, contains {self.sample_count()} samples in {len(self)} categories:\n{pformat([str(category) for category in self._categories.values()], indent=2)}"
