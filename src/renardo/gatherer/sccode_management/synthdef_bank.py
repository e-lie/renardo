import re
from pathlib import Path
from typing import Optional

from renardo.gatherer.sccode_management.synthdef_category import SynthDefCategory
from renardo.gatherer.sccode_management.synthdef_file_and_type import SynthDefType, SynthDefFile
from renardo.gatherer.sccode_management.synthdef_section import SynthDefSection


class SynthDefBank:
    """Represents a collection of instrument and effect categories."""
    def __init__(self, directory: Path):
        self.directory = directory
        self.name = self._parse_bank_name(directory.name)
        self.index = self._parse_bank_index(directory.name)

        # Initialize instruments and effects sections
        self.instruments = SynthDefSection(
            directory / SynthDefType.INSTRUMENT.value,
            SynthDefType.INSTRUMENT
        )
        self.effects = SynthDefSection(
            directory / SynthDefType.EFFECT.value,
            SynthDefType.EFFECT
        )

    @staticmethod
    def _parse_bank_name(dirname: str) -> str:
        """Extract bank name from directory name format: {index}_{name}."""
        match = re.match(r'\d+_(.+)', dirname)
        if not match:
            raise ValueError(f"Invalid bank directory format: {dirname}")
        return match.group(1)

    @staticmethod
    def _parse_bank_index(dirname: str) -> int:
        """Extract bank index from directory name format: {index}_{name}."""
        match = re.match(r'(\d+)_', dirname)
        if not match:
            raise ValueError(f"Invalid bank directory format: {dirname}")
        return int(match.group(1))

    def get_section(self, section_type: SynthDefType) -> SynthDefSection:
        """Get either the instruments or effects section."""
        if section_type == SynthDefType.INSTRUMENT:
            return self.instruments
        return self.effects

    def get_category(self, section_type: SynthDefType, category: str) -> Optional[SynthDefCategory]:
        """Get a category from either instruments or effects."""
        section = self.get_section(section_type)
        return section.get_category(category)

    def get_synthdef(self, section_type: SynthDefType, category: str, name: str) -> Optional[SynthDefFile]:
        """Get a specific synthdef by its section, category and name."""
        category_obj = self.get_category(section_type, category)
        if category_obj:
            return category_obj.get_synthdef(name)
        return None

    def __str__(self) -> str:
        return (f"SynthDefBank({self.index}: {self.name}, "
                f"{len(self.instruments)} instrument categories, "
                f"{len(self.effects)} effect categories)")
