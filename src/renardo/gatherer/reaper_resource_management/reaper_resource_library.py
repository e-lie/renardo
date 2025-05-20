from pathlib import Path
from collections import OrderedDict
from typing import List, Optional, Iterator, Dict, Any, TYPE_CHECKING
import re
import glob

from renardo.gatherer.reaper_resource_management.reaper_resource_bank import ReaperResourceBank
from renardo.lib.music_resource import ResourceType
from renardo.settings_manager import settings

# Avoid circular imports
# if TYPE_CHECKING:
#     from renardo.reaper_backend.reaper_music_resource import ReaperInstrument, ReaperEffect


class ReaperResourceLibrary:
    """Manages multiple Reaper resource banks in an ordered dictionary."""
    def __init__(self, root_directory: Path):
        self.root_directory = root_directory
        self._banks: OrderedDict[int, ReaperResourceBank] = OrderedDict()
        
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
        
        # First try to find directories with the pattern: digit_name
        indexed_dirs = [d for d in self.root_directory.iterdir() 
                    if d.is_dir() and re.match(r'\d+_', d.name)]
        
        # If we found indexed directories, use those
        if indexed_dirs:
            bank_dirs = sorted(
                indexed_dirs,
                key=lambda x: int(re.match(r'(\d+)_', x.name).group(1))
            )
        else:
            # Otherwise, use all directories (include those without index prefix)
            bank_dirs = [d for d in self.root_directory.iterdir() if d.is_dir()]
        
        for bank_dir in bank_dirs:
            try:
                bank = ReaperResourceBank(bank_dir)
                
                # Look for bank-specific configuration
                config_path = bank_dir / "config.py"
                if config_path.exists():
                    self._load_bank_config(bank, config_path)
                    
                self._banks[bank.index] = bank
            except Exception as e:
                print(f"Error loading bank from {bank_dir}: {e}")
                # Continue with next bank if one fails to load
    
    def _load_bank_config(self, bank: ReaperResourceBank, config_path: Path):
        """Load bank-specific configuration from a Python file."""
        try:
            local_scope = {}
            with open(config_path, 'r') as f:
                exec(f.read(), {}, local_scope)
            
            if 'default_arguments' in local_scope:
                bank.default_arguments = local_scope['default_arguments']
        except Exception as e:
            print(f"Error loading configuration from {config_path}: {e}")

    def get_bank(self, index: int) -> Optional[ReaperResourceBank]:
        """Get a bank by its index."""
        return self._banks.get(index)

    def get_bank_by_name(self, name: str) -> Optional[ReaperResourceBank]:
        """Get a bank by its name."""
        for bank in self._banks.values():
            if bank.name == name:
                return bank
        return None

    def list_banks(self) -> List[str]:
        """List all bank names."""
        return [bank.name for bank in self._banks.values()]

    def __iter__(self) -> Iterator[ReaperResourceBank]:
        return iter(self._banks.values())
    
    def find_fxchain_by_name(self, name: str) -> Optional[Path]:
        """
        Search for a fxchain file by name across all banks and categories.
        
        Args:
            name: The name of the fxchain file to search for (with or without .RfxChain extension)
            
        Returns:
            Path object to the fxchain file if found, None otherwise
        """
        # Normalize the name - ensure it has the .RfxChain extension
        if not name.lower().endswith('.rfxchain'):
            search_name = f"{name}.RfxChain"
        else:
            search_name = name
        
        # Get the lowercase version for case-insensitive comparison
        search_name_lower = search_name.lower()
        search_term = search_name_lower.replace('.rfxchain', '')
        
        # Resource types to search in
        resource_types = [ResourceType.EFFECT, ResourceType.INSTRUMENT]
        
        # First try exact matches across all banks and resource types
        for bank_index, bank in self._banks.items():
            for resource_type in resource_types:
                resource_dir = bank.directory / resource_type.value
                
                if not resource_dir.exists():
                    continue
                    
                # Search through all categories in the resource directory
                for category_dir in resource_dir.iterdir():
                    if not category_dir.is_dir():
                        continue
                        
                    # Check for exact match
                    fxchain_path = category_dir / search_name
                    if fxchain_path.exists():
                        return fxchain_path
                        
                    # Check for case-insensitive match
                    for file_path in category_dir.glob('*.RfxChain'):
                        # Case-insensitive exact name match
                        if file_path.name.lower() == search_name_lower:
                            return file_path
                        
        # If exact match not found, try partial match
        for bank_index, bank in self._banks.items():
            for resource_type in resource_types:
                resource_dir = bank.directory / resource_type.value
                
                if not resource_dir.exists():
                    continue
                    
                # Search through all categories in the resource directory
                for category_dir in resource_dir.iterdir():
                    if not category_dir.is_dir():
                        continue
                        
                    for file_path in category_dir.glob('*.RfxChain'):
                        # Partial match on filename
                        if search_term in file_path.stem.lower():
                            return file_path
        
        # Not found
        return None

def ensure_reaper_directories(renardo_root: Path):
    """Create the standard Reaper resource directory structure if it doesn't exist."""
    reaper_root = renardo_root / "reaper_resources"
    reaper_root.mkdir(exist_ok=True)
    
    # Create a basic bank structure if none exists
    if not any(d.is_dir() and re.match(r'\d+_', d.name) for d in reaper_root.iterdir()):
        # Create default banks
        banks = {
            "0_basic_resources": {
                "instruments": ["bass", "lead", "pads", "drums"],
                "effects": ["reverb", "delay", "modulation", "dynamics"]
            },
            "1_advanced_resources": {
                "instruments": ["analog", "digital", "hybrid"],
                "effects": ["creative", "mastering", "utility"]
            }
        }
        
        for bank_name, structure in banks.items():
            bank_dir = reaper_root / bank_name
            bank_dir.mkdir(exist_ok=True)
            
            # Create instrument categories
            instruments_dir = bank_dir / "instruments"
            instruments_dir.mkdir(exist_ok=True)
            
            for category in structure["instruments"]:
                category_dir = instruments_dir / category
                category_dir.mkdir(exist_ok=True)
                
                # Create a placeholder init file
                init_file = category_dir / "__init__.py"
                if not init_file.exists():
                    init_file.touch()
            
            # Create effect categories
            effects_dir = bank_dir / "effects"
            effects_dir.mkdir(exist_ok=True)
            
            for category in structure["effects"]:
                category_dir = effects_dir / category
                category_dir.mkdir(exist_ok=True)
                
                # Create a placeholder init file
                init_file = category_dir / "__init__.py"
                if not init_file.exists():
                    init_file.touch()
    
    return reaper_root

def ensure_reaper_directories():
    reaper_dir_path = settings.get_path("REAPER_LIBRARY")
    if not reaper_dir_path.exists():
        reaper_dir_path.mkdir(parents=True, exist_ok=True)
