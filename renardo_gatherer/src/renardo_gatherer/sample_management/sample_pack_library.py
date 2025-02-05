import re
from collections import OrderedDict
from pathlib import Path
import os
from os.path import isfile, isdir, splitext, join, abspath, isabs
from itertools import chain
from typing import Optional, List, Iterator
import fnmatch

from renardo_gatherer.sample_management.default_samples import default_loop_path
from renardo_gatherer.sample_management.sample_category import nonalpha
from renardo_gatherer.sample_management.sample_pack import SamplePack
from renardo_gatherer.sample_management.default_samples import DEFAULT_SAMPLES_PACK_NAME
from renardo_gatherer.config_dir import get_samples_dir_path

def hasext(filename):
    return bool(splitext(filename)[1])

supported_sound_file_extensions = ['wav', 'wave', 'aif', 'aiff', 'flac']

class SamplePackLibrary:
    """Manages multiple sample packs in an ordered dictionary."""
    def __init__(self, root_directory: Path, extra_paths: List[Path]=[]):
        self.root_directory = Path(root_directory)
        self._packs: OrderedDict[int, SamplePack] = OrderedDict()
        self._load_packs()
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

    def _get_sound_file(self, filename):
        """ Look for a file with all possible extensions """
        base, cur_ext = splitext(filename)
        if cur_ext:
            # If the filename already has an extensions, keep it
            if isfile(filename):
                return filename
        else:
            # Otherwise, look for all possible extensions
            for ext in supported_sound_file_extensions:
                # Look for .wav and .WAV
                for tryext in [ext, ext.upper()]:
                    extpath = filename + '.' + tryext
                    if isfile(extpath):
                        return extpath
        return None

    def _get_sound_file_or_dir(self, filename):
        """ Get a matching sound file or directory """
        if isdir(filename):
            return abspath(filename)
        foundfile = self._get_sound_file(filename)
        if foundfile:
            return abspath(foundfile)
        return None

    def _search_paths(self, filename):
        """ Search our search paths for an audio file or directory """
        if isabs(filename):
            return self._get_sound_file_or_dir(filename)
        else:
            for root in self._extra_paths:
                fullpath = join(root, filename)
                foundfile = self._get_sound_file_or_dir(fullpath)
                if foundfile:
                    return foundfile
        return None

    def _get_file_in_dir(self, dirname, index):
        """ Return nth sample in a directory """
        candidates = []
        for filename in sorted(os.listdir(dirname)):
            name, ext = splitext(filename)
            if 'Placeholder' in name:
                continue
            if ext.lower()[1:] in supported_sound_file_extensions:
                fullpath = join(dirname, filename)
                if len(candidates) == index:
                    return fullpath
                candidates.append(fullpath)
        if candidates:
            return candidates[int(index) % len(candidates)]
        return None

    def _pattern_search(self, filename, index):
        """
        Return nth sample that matches a path pattern

        Path pattern is a relative path that can contain wildcards such as *
        and ? (see fnmatch for more details). Some example paths:

            samp*
            **/voices/*
            perc*/bass*

        """

        def _find_next_subpaths(path, pattern):
            """ For a path pattern, find all subpaths that match """
            # ** is a special case meaning "all recursive directories"
            if pattern == '**':
                for dirpath, _, _ in os.walk(path):
                    yield dirpath
            else:
                children = os.listdir(path)
                for c in fnmatch.filter(children, pattern):
                    yield join(path, c)

        candidates = []
        queue = self._extra_paths[:]
        subpaths = filename.split(os.sep)
        filepat = subpaths.pop()
        while subpaths:
            subpath = subpaths.pop(0)
            queue = list(chain.from_iterable(
                (_find_next_subpaths(p, subpath) for p in queue)
            ))

        # If the filepat (ex. 'foo*.wav') has an extension, we want to match
        # the full filename. If not, we just match against the basename.
        match_base = not hasext(filepat)

        for path in queue:
            for subpath, _, filenames in os.walk(path):
                for filename in sorted(filenames):
                    basename, ext = splitext(filename)
                    if ext[1:].lower() not in supported_sound_file_extensions:
                        continue
                    if match_base:
                        ismatch = fnmatch.fnmatch(basename, filepat)
                    else:
                        ismatch = fnmatch.fnmatch(filename, filepat)
                    if ismatch:
                        fullpath = join(subpath, filename)
                        if len(candidates) == index:
                            return fullpath
                        candidates.append(fullpath)
        if candidates:
            return candidates[index % len(candidates)]
        return None

    def _find_sample(self, sample_glob: str, index=0):
        """
        Find a sample from a filename or pattern

        Will first attempt to find an exact match (by abspath or relative to
        the search paths). Then will attempt to pattern match in search paths.

        """
        path = self._search_paths(sample_glob)
        if path:
            # If it's a file, use that sample
            if isfile(path):
                return path
            # If it's a dir, use one of the samples in that dir
            elif isdir(path):
                foundfile = self._get_file_in_dir(path, index)
                if foundfile:
                    return foundfile
                else:
                    # WarningMsg("No sound files in %r" % path)
                    return None
            else:
                # WarningMsg("File %r is neither a file nor a directory" % path)
                return None
        else:
            # If we couldn't find a dir or file with this name, then we use it
            # as a pattern and recursively walk our paths
            foundfile = self._pattern_search(sample_glob, index)
            if foundfile:
                return foundfile
            # WarningMsg("Could not find any sample matching %r" % filename)
            return None

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
