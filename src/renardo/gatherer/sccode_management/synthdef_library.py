from pathlib import Path
from collections import OrderedDict
from typing import List, Optional, Iterator
import re

from renardo.gatherer.sccode_management.synthdef_bank import SynthDefBank
from renardo.gatherer.sccode_management.synthdef_file_and_type import SynthDefType


class SynthDefLibrary:
    """Manages multiple synthdef banks in an ordered dictionary."""
    def __init__(self, root_directory: Path):
        self.root_directory = Path(root_directory)
        self._banks: OrderedDict[int, SynthDefBank] = OrderedDict()
        self._load_banks()
    
    def _load_banks(self):
        """Load all synthdef banks from the root directory."""
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
                bank = SynthDefBank(bank_dir)
                self._banks[bank.index] = bank
            except ValueError as e:
                print(f"Warning: Skipping invalid bank directory {bank_dir}: {e}")
    
    def get_bank(self, index: int) -> Optional[SynthDefBank]:
        """Get a synthdef bank by its index."""
        return self._banks.get(index)
    
    def get_bank_by_name(self, name: str) -> Optional[SynthDefBank]:
        """Get a synthdef bank by its name."""
        for bank in self._banks.values():
            if bank.name == name:
                return bank
        return None
    
    def list_banks(self) -> List[str]:
        """List all bank names with their indices."""
        return [f"{bank.index}: {bank.name}" for bank in self._banks.values()]
    
    def __len__(self) -> int:
        return len(self._banks)
    
    def __iter__(self) -> Iterator[SynthDefBank]:
        return iter(self._banks.values())

