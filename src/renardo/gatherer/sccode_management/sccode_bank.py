import re
from pathlib import Path
from typing import Optional

from renardo.gatherer.sccode_management.sccode_category import SCCodeCategory
from renardo.gatherer.sccode_management.sc_resource import SCResourceType
from renardo.gatherer.sccode_management.sccode_section import SCCodeSection


class SCCodeBank:
    """Represents a collection of instrument and effect categories."""
    def __init__(self, directory: Path):
        self.directory = directory
        self.name = self._parse_bank_name(directory.name)
        self.index = self._parse_bank_index(directory.name)
        self.default_arguments = {}

        # Initialize instruments and effects sections
        self.instruments = SCCodeSection(
            directory / SCResourceType.INSTRUMENT.value,
            SCResourceType.INSTRUMENT
        )
        self.effects = SCCodeSection(
            directory / SCResourceType.EFFECT.value,
            SCResourceType.EFFECT
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

    def get_section(self, section_type: SCResourceType) -> SCCodeSection:
        """Get either the instruments or effects section."""
        if section_type == SCResourceType.INSTRUMENT:
            return self.instruments
        return self.effects

    def get_category(self, section_type: SCResourceType, category: str) -> Optional[SCCodeCategory]:
        """Get a category from either instruments or effects."""
        section = self.get_section(section_type)
        return section.get_category(category)

    # def get_synthdef(self, section_type: SCResourceType, category: str, name: str) -> Optional[SCCodeFile]:
    #     """Get a specific synthdef by its section, category and name."""
    #     category_obj = self.get_category(section_type, category)
    #     if category_obj:
    #         return category_obj.get_synthdef(name)
    #     return None

    def __str__(self) -> str:
        return (f"SynthDefBank({self.index}: {self.name}, "
                f"{len(self.instruments)} instrument categories, "
                f"{len(self.effects)} effect categories)")
