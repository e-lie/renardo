import re
from collections import OrderedDict
from pathlib import Path
#import os
#from os.path import isfile, isdir, splitext, join, abspath, isabs
from typing import Optional, List, Iterator

from renardo_gatherer.sample_management.default_samples import default_loop_path
from renardo_gatherer.sample_management.sample_category import nonalpha
from renardo_gatherer.sample_management.sample_pack import SamplePack
#from renardo_gatherer.sample_management.default_samples import DEFAULT_SAMPLES_PACK_NAME
from renardo_gatherer.config_dir import get_samples_dir_path

#def hasext(filename):
#    return bool(splitext(filename)[1])

#supported_sound_file_extensions = ['wav', 'wave', 'aif', 'aiff', 'flac']

class SamplePackLibrary:
    """Manages multiple sample packs in an ordered dictionary."""
    def __init__(self, root_directory: Path, extra_paths: List[Path]=[]):
        self.root_directory = Path(root_directory)
        self._packs: OrderedDict[int, SamplePack] = OrderedDict()
        self._load_packs()
        self._extra_paths = [Path(p) for p in extra_paths]
        self._extra_paths = extra_paths + [default_loop_path()]

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

    def sample_category_path_from_symbol(self, symbol: str, spack=0):
        category = nonalpha[symbol] if symbol in nonalpha.keys() else symbol
        return self.get_pack(spack).get_category(category).directory

    def _find_sample(self, sample_glob: str, index: int = 0) -> Optional[Path]:
        """
        Find a sample file by name, category/symbol, or pattern.
        If multiple matches are found (e.g., in a directory), returns the nth match
        based on the index parameter.

        Search order:
        1. Try as absolute path
        2. Search in sample packs by category/symbol
        3. Look for directory with matching name and get nth sample
        4. Search in extra paths as relative path
        5. Try pattern matching in extra paths

        Args:
            sample_glob: Sample identifier (can be path, category, or pattern)
            index: Index of the sample to return when multiple matches found (default: 0)

        Returns:
            Path to the sample if found, None otherwise
        """
        # First try to interpret as an absolute path
        path = Path(sample_glob)
        if path.is_absolute():
            if path.is_dir():
                samples = self._find_samples_in_directory(path)
                if samples:
                    return samples[index % len(samples)]
            else:
                result = self._find_exact_file(path)
                if result:
                    return result

        # Try to find in sample packs by category/symbol
        for pack in self._packs.values():
            # Check if it's a category name
            category = pack.get_category(sample_glob)
            if category:
                samples = list(category)
                if samples:
                    return samples[index % len(samples)].full_path

        # Look for directory with matching name in extra paths
        for base_path in self._extra_paths:
            for dir_path in base_path.iterdir():
                if dir_path.is_dir() and dir_path.name == sample_glob:
                    # Found matching directory, get nth sample
                    samples = self._find_samples_in_directory(dir_path)
                    if samples:
                        return samples[index % len(samples)]

        # Try as relative path in extra paths
        for base_path in self._extra_paths:
            full_path = base_path / sample_glob
            if full_path.is_dir():
                samples = self._find_samples_in_directory(full_path)
                if samples:
                    return samples[index % len(samples)]
            else:
                result = self._find_exact_file(full_path)
                if result:
                    return result

        # Try pattern matching in extra paths
        all_matches = []
        for base_path in self._extra_paths:
            matches = self._find_pattern_matches(base_path, sample_glob)
            all_matches.extend(matches)

        if all_matches:
            return sorted(all_matches)[index % len(all_matches)]

        return None

    def _find_samples_in_directory(self, directory: Path) -> List[Path]:
        """Find all sample files in a directory, sorted alphabetically."""
        return sorted([
            path for path in directory.iterdir()
            if path.is_file() and self._is_valid_audio_file(path)
        ])

    def _find_exact_file(self, path: Path) -> Optional[Path]:
        """Find an exact file match, trying different extensions if needed."""
        # If path has extension, try exact match
        if path.suffix:
            if path.is_file() and self._is_valid_audio_file(path):
                return path
            return None

        # Try all possible extensions
        for ext in self._get_audio_extensions():
            with_ext = path.with_suffix(f".{ext}")
            if with_ext.is_file():
                return with_ext

        return None

    def _find_pattern_matches(self, base_path: Path, pattern: str) -> List[Path]:
        """Find all files matching a glob pattern."""
        matches = []

        # Handle **/ pattern specially
        if "**" in pattern:
            # Replace **/ with recursive glob
            pattern = pattern.replace("**/", "")
            glob_pattern = f"**/{pattern}"
        else:
            glob_pattern = pattern

        # Find all matching files
        for path in sorted(base_path.rglob(glob_pattern)):
            if path.is_file() and self._is_valid_audio_file(path):
                matches.append(path)

        return matches

    @staticmethod
    def _get_audio_extensions() -> List[str]:
        """Get list of supported audio file extensions."""
        extentions =  ['wav', 'wave', 'aif', 'aiff', 'flac']
        return extentions + [extention.upper() for extention in extentions]

    @staticmethod
    def _is_valid_audio_file(path: Path) -> bool:
        """Check if file has a supported audio extension."""
        return path.suffix.lower()[1:] in SamplePackLibrary._get_audio_extensions()


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


SAMPLES_DIR_PATH = get_samples_dir_path()
sample_pack_library = SamplePackLibrary(SAMPLES_DIR_PATH, [])

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
    sample_packs = SamplePackLibrary(root_dir)
    print(sample_packs[0])

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
