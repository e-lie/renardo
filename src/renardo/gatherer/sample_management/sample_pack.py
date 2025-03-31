import re
from pathlib import Path
from pprint import pformat
from typing import Dict, Optional, List, Iterator

from renardo.gatherer.sample_management.sample_category import SampleCategory, nonalpha, alpha
from renardo.gatherer.sample_management.sample_file import SampleFile
from renardo.gatherer.sample_management.default_samples import LOOP_SUBDIR


class SamplePack:
    """Represents a collection of categorized samples in a directory."""
    def __init__(self, directory: Path):
        self.directory = directory
        self._categories: Dict[str, SampleCategory] = {}
        self.name = self._parse_pack_name(directory.name)
        self.index = self._parse_pack_index(directory.name)
        self._load_categories()
        self.complete = self._is_complete()

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
        category_fullname = nonalpha[category] if category in nonalpha.keys() else category
        return self._categories.get(category_fullname)

    def get_sample(self, category: str, index: int) -> Optional[SampleFile]:
        """Get a sample by its category and index."""
        category_obj = self.get_category(category)
        if category_obj:
            return category_obj.get_sample(index)
        return None

    def _is_complete(self) -> bool:
        "check if every basic symbol/letter is provided with a sample"
        # IMPROVE define what complete means and effectively check if there is a sample in each category
        complete = True
        all_base_categories = list(alpha) + list(alpha.upper()) + list(nonalpha.values()) + [LOOP_SUBDIR]
        for cat in all_base_categories:
            if cat not in self._categories.keys():
                complete = False
        return complete

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
