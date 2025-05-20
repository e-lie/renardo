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
        
        # Find instrument directory (case-insensitive)
        instrument_dir = self._find_directory_case_insensitive(directory, ResourceType.INSTRUMENT.value)
        print(f"Found instrument directory: {instrument_dir}")
        
        # Find effect directory (case-insensitive)
        effect_dir = self._find_directory_case_insensitive(directory, ResourceType.EFFECT.value)
        print(f"Found effect directory: {effect_dir}")

        # Initialize instruments and effects sections
        self.instruments = ReaperResourceSection(
            instrument_dir,
            ResourceType.INSTRUMENT
        )
        
        self.effects = ReaperResourceSection(
            effect_dir,
            ResourceType.EFFECT
        )
        
    def _find_directory_case_insensitive(self, parent_dir: Path, dir_name: str) -> Path:
        """Find a directory by name, ignoring case."""
        # Make sure the parent directory exists
        if not parent_dir.exists() or not parent_dir.is_dir():
            print(f"Parent directory does not exist: {parent_dir}")
            return parent_dir / dir_name
            
        # First check for exact match
        exact_match = parent_dir / dir_name
        if exact_match.exists() and exact_match.is_dir():
            return exact_match
            
        # Check for case-insensitive match
        for item in parent_dir.iterdir():
            if item.is_dir() and item.name.lower() == dir_name.lower():
                print(f"Found case-insensitive match for {dir_name}: {item.name}")
                return item
                
        # Finally, also check for singular/plural variations
        plural_forms = {
            "instrument": "instruments",
            "effect": "effects"
        }
        
        if dir_name in plural_forms:
            plural_name = plural_forms[dir_name]
            # Check for plural form
            plural_match = parent_dir / plural_name
            if plural_match.exists() and plural_match.is_dir():
                print(f"Found plural form for {dir_name}: {plural_name}")
                return plural_match
                
            # Check for plural form with different case
            for item in parent_dir.iterdir():
                if item.is_dir() and item.name.lower() == plural_name.lower():
                    print(f"Found case-insensitive plural match for {dir_name}: {item.name}")
                    return item
        
        # If no match found, return the original (even if it doesn't exist)
        return parent_dir / dir_name

    @staticmethod
    def _parse_bank_name(dirname: str) -> str:
        """Extract bank name from directory name format: {index}_{name}."""
        match = re.match(r'\d+_(.+)', dirname)
        if not match:
            # If there's no index prefix, use the entire directory name
            return dirname
        return match.group(1)

    @staticmethod
    def _parse_bank_index(dirname: str) -> int:
        """Extract bank index from directory name format: {index}_{name}."""
        match = re.match(r'(\d+)_', dirname)
        if not match:
            # If there's no index prefix, use 0 as default
            return 0
        return int(match.group(1))

    def get_section(self, section_type: ResourceType) -> ReaperResourceSection:
        """Get either the instruments or effects section."""
        if section_type == ResourceType.INSTRUMENT:
            return self.instruments
        return self.effects

    def get_resource(self, section_type: ResourceType, category: str, name: str) -> Optional[ReaperResourceFile]:
        """Get a specific resource from the bank."""
        section = self.get_section(section_type)
        # Debug
        print(f"Looking for resource {name} in category {category} of section {section_type.value}")
        
        resource = section.get_resource(category, name)
        if resource:
            print(f"Resource found: {resource}")
        else:
            print(f"Resource not found in {section_type.value}/{category}")
            
        return resource

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