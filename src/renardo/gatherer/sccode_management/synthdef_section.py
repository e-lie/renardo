from pathlib import Path
from typing import Dict, Optional, List, Iterator

from renardo.gatherer.sccode_management.synthdef_category import SynthDefCategory
from renardo.gatherer.sccode_management.synthdef_file_and_type import SynthDefType


class SynthDefSection:
    """Represents either the instruments or effects section of a bank."""
    def __init__(self, directory: Path, synth_type: SynthDefType):
        self.directory = directory
        self.type = synth_type
        self._categories: Dict[str, SynthDefCategory] = {}
        self._load_categories()

    def _load_categories(self):
        """Load all categories in this section."""
        if not self.directory.exists():
            return

        for category_dir in self.directory.iterdir():
            if category_dir.is_dir():
                category = category_dir.name
                self._categories[category] = SynthDefCategory(
                    category_dir,
                    category,
                    self.type
                )

    def get_category(self, category: str) -> Optional[SynthDefCategory]:
        """Get a category by its name."""
        return self._categories.get(category)

    def list_categories(self) -> List[str]:
        """List all category names."""
        return list(self._categories.keys())

    def __len__(self) -> int:
        return len(self._categories)

    def __iter__(self) -> Iterator[SynthDefCategory]:
        return iter(self._categories.values())

    def __str__(self) -> str:
        return f"SynthDefSection({self.type.value}, {len(self)} categories)"
