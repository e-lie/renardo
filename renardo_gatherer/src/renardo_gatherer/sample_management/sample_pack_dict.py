import re
from collections import OrderedDict
from pathlib import Path
from typing import Optional, List, Iterator

from .sample_pack import SamplePack
from .default_samples import DEFAULT_SAMPLES_PACK_NAME
from renardo_gatherer.config_dir import get_samples_dir_path

SAMPLES_DIR_PATH = get_samples_dir_path()

nonalpha = {"&": "ampersand",
            "*": "asterix",
            "@": "at",
            "\\": "backslash",
            "|": "bar",
            "^": "caret",
            ":": "colon",
            "$": "dollar",
            "=": "equals",
            "!": "exclamation",
            "/": "forwardslash",
            "#": "hash",
            "-": "hyphen",
            "<": "lessthan",
            "%": "percent",
            "+": "plus",
            "?": "question",
            ";": "semicolon",
            "~": "tilde",
            ",": "comma",
            "0": "0",
            "1": "1",
            "2": "2",
            "3": "3",
            "4": "4",
            "5": "5",
            "6": "6",
            "7": "7",
            "8": "8",
            "9": "9"}

class SamplePackDict:
    """Manages multiple sample packs in an ordered dictionary."""
    def __init__(self, root_directory: Path):
        self.root_directory = Path(root_directory)
        self._packs: OrderedDict[int, SamplePack] = OrderedDict()
        self._load_packs()

    def _load_packs(self):
        """Load all sample packs from the root directory."""
        if not self.root_directory.exists():
            raise FileNotFoundError(f"Root directory not found: {self.root_directory}")

        # Find all directories matching the pattern: digit_name
        pack_dirs = sorted(
            [d for d in self.root_directory.iterdir()
             if d.is_dir() and re.match(r'\d+_', d.name)],
            key=lambda x: int(re.match(r'(\d+)_', x.name).group(1))
        )

        # Load each pack
        for pack_dir in pack_dirs:
            try:
                pack = SamplePack(pack_dir)
                self._packs[pack.index] = pack
            except ValueError as e:
                print(f"Warning: Skipping invalid pack directory {pack_dir}: {e}")

    def get_pack(self, index: int) -> Optional[SamplePack]:
        """Get a sample pack by its index."""
        return self._packs.get(index)

    def get_pack_by_name(self, name: str) -> Optional[SamplePack]:
        """Get a sample pack by its name."""
        for pack in self._packs.values():
            if pack.name == name:
                return pack
        return None

    def list_packs(self) -> List[str]:
        """List all pack names with their indices."""
        return [f"{pack.index}: {pack.name}" for pack in self._packs.values()]

    def __len__(self) -> int:
        return len(self._packs)

    def __iter__(self) -> Iterator[SamplePack]:
        return iter(self._packs.values())

    def __getitem__(self, index: int) -> SamplePack:
        if index not in self._packs:
            raise KeyError(f"No sample pack with index {index}")
        return self._packs[index]



def ensure_renardo_samples_directory():
    if not SAMPLES_DIR_PATH.exists():
        SAMPLES_DIR_PATH.mkdir(parents=True, exist_ok=True)


def sample_path_from_symbol(symbol: str, spack_path=SAMPLES_DIR_PATH / DEFAULT_SAMPLES_PACK_NAME):
    """ Return the sample search directory for a symbol """
    sample_path = None
    if symbol.isalpha():
        low_up_dirname = 'upper' if symbol.isupper() else 'lower'
        sample_path = spack_path / symbol.lower() / low_up_dirname
    elif symbol in nonalpha:
        longname = nonalpha[symbol]
        sample_path = spack_path / '_' / longname
    return sample_path


# Example usage
if __name__ == "__main__":
    # Example directory structure:
    # sample_packs/
    #   0_drum_kit/
    #     k/  # kick drums
    #       kick_0.wav
    #       kick_1.wav
    #     s/  # snares
    #       snare_0.wav
    #       snare_1.wav
    #     h/  # hi-hats
    #       hihat_0.wav
    #       hihat_1.wav

    root_dir = get_samples_dir_path()
    sample_packs = SamplePackDict(root_dir)

    # List all packs
    print("Available sample packs:")
    for pack_name in sample_packs.list_packs():
        print(f"  {pack_name}")

    # Get a specific pack
    pack = sample_packs.get_pack(0)
    if pack:
        print(f"\nCategories in {pack.name}:")
        for category in pack:
            print(f"  {category}")
            for sample in category:
                print(f"    {sample}")
