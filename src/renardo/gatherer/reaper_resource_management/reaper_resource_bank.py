import re
from pathlib import Path
from typing import Optional

from renardo.gatherer.reaper_resource_management.reaper_resource_category import ReaperResourceCategory
from renardo.gatherer.reaper_resource_management.reaper_resource_file import ReaperResourceFile
from renardo.gatherer.reaper_resource_management.reaper_resource_section import ReaperResourceSection
from renardo.lib.music_resource import ResourceType


class ReaperResourceBank:
    """Represents a collection of instrument and effect categories."""
    def __init__(self, directory: Path):
        self.directory = directory
        self.name = self._parse_bank_name(directory.name)
        self.index = self._parse_bank_index(directory.name)
        self.default_arguments = {}

        # Initialize instruments and effects sections
        self.instruments = ReaperResourceSection(
            directory / ResourceType.INSTRUMENT.value,
            ResourceType.INSTRUMENT
        )
        self.effects = ReaperResourceSection(
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

    def get_section(self, section_type: ResourceType) -> ReaperResourceSection:
        """Get either the instruments or effects section."""
        if section_type == ResourceType.INSTRUMENT:
            return self.instruments
        return self.effects

    def get_resource(self, section_type: ResourceType, category: str, name: str) -> Optional[ReaperResourceFile]:
        """Get a specific resource from the bank."""
        section = self.get_section(section_type)
        return section.get_resource(category, name)

    def list_categories(self, section_type: ResourceType) -> list[str]:
        """List all categories in a section."""
        section = self.get_section(section_type)
        return section.list_categories()

    def list_resources(self, section_type: ResourceType, category: str) -> list[str]:
        """List all resources in a category."""
        section = self.get_section(section_type)
        category_obj = section.get_category(category)
        if category_obj:
            return category_obj.list_resources()
        return []

    def __str__(self) -> str:
        return f"ReaperResourceBank({self.index}_{self.name})"