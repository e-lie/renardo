from pathlib import Path
from typing import Dict, Optional, List, Tuple, Iterator

from renardo_gatherer.sample_management.sample_file import SampleFile


alpha    = "abcdefghijklmnopqrstuvwxyz"
nonalpha = {"&": "_ampersand",
            "*": "_asterix",
            "@": "_at",
            "\\": "_backslash",
            "|": "_bar",
            "^": "_caret",
            ":": "_colon",
            "$": "_dollar",
            "=": "_equals",
            "!": "_exclamation",
            "/": "_forwardslash",
            "#": "_hash",
            "-": "_hyphen",
            "<": "_lessthan",
            "%": "_percent",
            "+": "_plus",
            "?": "_question",
            ";": "_semicolon",
            "~": "_tilde",
            ",": "_comma",
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

class SampleCategory:
    """Represents a collection of indexed samples under a letter/symbol category."""
    def __init__(self, directory: Path, category: str):
        self.directory = directory
        self.category = category
        self._samples: Dict[int, SampleFile] = {}
        self._load_samples()

    def _load_samples(self):
        """Load all audio samples from the category directory, using alphabetical order for indices."""
        audio_extensions = {'.wav', '.aif', '.aiff', '.mp3', '.flac', '.ogg'}

        # Get all audio files and sort them alphabetically
        audio_files = sorted([
            f for f in self.directory.iterdir()
            if f.is_file() and f.suffix.lower() in audio_extensions
        ])

        # Assign indices based on sorted order
        for index, file_path in enumerate(audio_files):
            sample = SampleFile(file_path, self.category, index)
            self._samples[index] = sample

    def get_sample(self, index: int) -> Optional[SampleFile]:
        """Get a sample by its index."""
        return self._samples.get(index)

    def list_samples(self) -> List[Tuple[int, str]]:
        """List all sample indices and names."""
        return [(idx, sample.name) for idx, sample in self._samples.items()]

    def __len__(self) -> int:
        return len(self._samples)

    def __iter__(self) -> Iterator[SampleFile]:
        return iter(self._samples.values())

    def __str__(self) -> str:
        return f"SampleCategory({self.category}, {len(self)} samples)"

