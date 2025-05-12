from pathlib import Path
from collections import OrderedDict
from typing import List, Optional, Iterator, Dict, Any
import re

from renardo.gatherer.sccode_management.scresource_bank import SCResourceBank
from renardo.gatherer.sccode_management.sc_resource import SCInstrument, SCEffect
from renardo.lib.music_resource import ResourceType
from renardo.settings_manager import settings


class SCResourceLibrary:
    """Manages multiple synthdef banks in an ordered dictionary."""
    def __init__(self, root_directory: Path):
        self.root_directory = root_directory
        self._banks: OrderedDict[int, SCResourceBank] = OrderedDict()
        
        # Global default arguments that apply to all banks
        self.global_defaults: Dict[str, Any] = {}
        
        # Look for a global_config.py file
        global_config_path = self.root_directory / "global_config.py"
        if global_config_path.exists():
            self._load_global_config(global_config_path)
            
        self._load_banks()
    
    def _load_global_config(self, config_path: Path):
        """Load global configuration from a Python file."""
        try:
            local_scope = {}
            with open(config_path, 'r') as f:
                exec(f.read(), {}, local_scope)
            
            if 'global_defaults' in local_scope:
                self.global_defaults = local_scope['global_defaults']
        except Exception as e:
            print(f"Error loading global configuration from {config_path}: {e}")
    
    def _load_banks(self):
        """Load all banks from the root directory."""
        if not self.root_directory.exists():
            raise FileNotFoundError(f"Root directory not found: {self.root_directory}")
        
        # Find all directories matching the pattern: digit_name
        bank_dirs = sorted(
            [d for d in self.root_directory.iterdir() 
             if d.is_dir() and re.match(r'\d+_', d.name)],
            key=lambda x: int(re.match(r'(\d+)_', x.name).group(1))
        )
        
        # Load each bank
        for bank_dir in bank_dirs:
            try:
                bank = SCResourceBank(bank_dir)
                self._banks[bank.index] = bank
            except ValueError as e:
                print(f"Warning: Skipping invalid bank directory {bank_dir}: {e}")
    
    def get_bank(self, index: int) -> Optional[SCResourceBank]:
        """Get a synthdef bank by its index."""
        return self._banks.get(index)
    
    def get_bank_by_name(self, name: str) -> Optional[SCResourceBank]:
        """Get a synthdef bank by its name."""
        for bank in self._banks.values():
            if bank.name == name:
                return bank
        return None
    
    def get_resource(self, bank_index: int, section_type: ResourceType, category: str, name: str):
        """Get a specific resource by its bank, section, category and name."""
        bank = self.get_bank(bank_index)
        if bank:
            return bank.get_resource(section_type, category, name)
        return None
    
    def list_banks(self) -> List[str]:
        """List all bank names with their indices."""
        return [f"{bank.index}: {bank.name}" for bank in self._banks.values()]
    
    def __len__(self) -> int:
        return len(self._banks)
    
    def __iter__(self) -> Iterator[SCResourceBank]:
        return iter(self._banks.values())
        
    def find_resources(self, query: str, section_type: Optional[ResourceType] = None) -> List[Dict[str, Any]]:
        """
        Search for resources by name or description.
        
        Args:
            query: The search string to look for in resource names and descriptions
            section_type: Optional filter by section type (instrument or effect)
            
        Returns:
            A list of dictionaries with found resources and their metadata
        """
        query = query.lower()
        results = []
        
        for bank in self._banks.values():
            sections = []
            if section_type:
                sections = [bank.get_section(section_type)]
            else:
                sections = [bank.instruments, bank.effects]
                
            for section in sections:
                for category in section:
                    for resource in category:
                        if (query in resource.shortname.lower() or 
                            query in resource.fullname.lower() or 
                            query in resource.description.lower()):
                            
                            results.append({
                                "bank": bank.name,
                                "bank_index": bank.index,
                                "section": section.type.value,
                                "category": category.category,
                                "shortname": resource.shortname,
                                "fullname": resource.fullname,
                                "description": resource.description,
                                "arguments": resource.arguments
                            })
        
        return results


def ensure_sccode_directories():
    sccode_dir_path = settings.get_path("SCCODE_LIBRARY")
    if not sccode_dir_path.exists():
        sccode_dir_path.mkdir(parents=True, exist_ok=True)
    special_sccode_dir_path = settings.get_path("SPECIAL_SCCODE_DIR")
    if not special_sccode_dir_path.exists():
        special_sccode_dir_path.mkdir(parents=True, exist_ok=True)