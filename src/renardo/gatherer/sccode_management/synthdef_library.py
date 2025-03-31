from pathlib import Path
from collections import OrderedDict
from typing import Dict, List, Optional, Iterator, Literal
import re
from enum import Enum

class SynthDefType(Enum):
    INSTRUMENT = "instruments"
    EFFECT = "effects"

class SynthDefFile:
    """Represents a single SuperCollider synthdef file."""
    def __init__(self, path: Path, synth_type: SynthDefType, category: str):
        self.path = path
        self.name = path.stem
        self.extension = path.suffix
        self.size = path.stat().st_size
        self.type = synth_type
        self.category = category
        
    @property
    def full_path(self) -> Path:
        return self.path
    
    def __str__(self) -> str:
        return f"SynthDefFile({self.type.value}/{self.category}/{self.name})"
    
    def __repr__(self) -> str:
        return self.__str__()

class SynthDefCategory:
    """Represents a collection of synthdefs in a category (e.g., 'bass', 'lead' or 'reverb', 'delay')."""
    def __init__(self, directory: Path, category: str, synth_type: SynthDefType):
        self.directory = directory
        self.category = category
        self.type = synth_type
        self._synthdefs: Dict[str, SynthDefFile] = {}
        self._load_synthdefs()
    
    def _load_synthdefs(self):
        """Load all synthdef files from the category directory."""
        synthdef_extensions = {'.scsyndef'}  # SuperCollider compiled synthdef extension
        scd_extensions = {'.scd', '.sc'}     # SuperCollider source file extensions
        
        for file_path in self.directory.iterdir():
            if file_path.is_file():
                if file_path.suffix.lower() in synthdef_extensions:
                    synthdef = SynthDefFile(file_path, self.type, self.category)
                    self._synthdefs[synthdef.name] = synthdef
                elif file_path.suffix.lower() in scd_extensions:
                    # Handle SuperCollider source files if needed
                    pass
    
    def get_synthdef(self, name: str) -> Optional[SynthDefFile]:
        """Get a synthdef by its name."""
        return self._synthdefs.get(name)
    
    def list_synthdefs(self) -> List[str]:
        """List all synthdef names in this category."""
        return list(self._synthdefs.keys())
    
    def __len__(self) -> int:
        return len(self._synthdefs)
    
    def __iter__(self) -> Iterator[SynthDefFile]:
        return iter(self._synthdefs.values())
    
    def __str__(self) -> str:
        return f"SynthDefCategory({self.type.value}/{self.category}, {len(self)} synthdefs)"

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

# Example usage
if __name__ == "__main__":
    # Example directory structure:
    # synthdefs/
    #   0_basic_synths/
    #     instruments/
    #       bass/
    #         sub_bass.scsyndef
    #         wobble_bass.scsyndef
    #       lead/
    #         saw_lead.scsyndef
    #     effects/
    #       reverb/
    #         plate_reverb.scsyndef
    #       delay/
    #         tape_delay.scsyndef
    
    root_dir = Path("./synthdefs")
    library = SynthDefLibrary(root_dir)
    
    # List all banks
    print("Available synthdef banks:")
    for bank_name in library.list_banks():
        print(f"  {bank_name}")
    
    # Get a specific bank
    bank = library.get_bank(0)
    if bank:
        print(f"\nBank: {bank.name}")
        
        print("\nInstrument categories:")
        for category in bank.instruments:
            print(f"  {category}")
            for synthdef in category:
                print(f"    {synthdef}")
                
        print("\nEffect categories:")
        for category in bank.effects:
            print(f"  {category}")
            for synthdef in category:
                print(f"    {synthdef}")
        
        # Get a specific instrument
        bass = bank.get_synthdef(SynthDefType.INSTRUMENT, "bass", "sub_bass")
        if bass:
            print(f"\nFound instrument: {bass}")
            
        # Get a specific effect
        reverb = bank.get_synthdef(SynthDefType.EFFECT, "reverb", "plate_reverb")
        if reverb:
            print(f"Found effect: {reverb}")