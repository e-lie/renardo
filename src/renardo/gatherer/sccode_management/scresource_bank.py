import re
from pathlib import Path
from typing import Optional

from renardo.gatherer.sccode_management.scresource_category import SCResourceCategory
from renardo.gatherer.sccode_management.scresource_type_and_file import SCResourceFile
from renardo.gatherer.sccode_management.scresource_section import SCResourceSection
from renardo.lib.music_resource import ResourceType


class SCResourceBank:
    """Represents a collection of instrument and effect categories."""
    def __init__(self, directory: Path):
        self.directory = directory
        self.name = self._parse_bank_name(directory.name)
        self.index = self._parse_bank_index(directory.name)
        self.default_arguments = {}

        # Initialize instruments and effects sections
        self.instruments = SCResourceSection(
            directory / ResourceType.INSTRUMENT.value,
            ResourceType.INSTRUMENT
        )
        self.effects = SCResourceSection(
            directory / ResourceType.EFFECT.value,
            ResourceType.EFFECT
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

    def get_section(self, section_type: ResourceType) -> SCResourceSection:
        """Get either the instruments or effects section."""
        if section_type == ResourceType.INSTRUMENT:
            return self.instruments
        return self.effects

    def get_category(self, section_type: ResourceType, category: str) -> Optional[SCResourceCategory]:
        """Get a category from either instruments or effects."""
        section = self.get_section(section_type)
        return section.get_category(category)

    def get_synthdef(self, section_type: ResourceType, category: str, name: str) -> Optional[SCResourceFile]:
        """Get a specific synthdef by its section, category and name."""
        category_obj = self.get_category(section_type, category)
        if category_obj:
            return category_obj.get_resource(name)
        return None

    def __str__(self) -> str:
        return (f"SCResourceBank({self.index}: {self.name}, "
                f"{len(self.instruments)} instrument categories, "
                f"{len(self.effects)} effect categories)")
