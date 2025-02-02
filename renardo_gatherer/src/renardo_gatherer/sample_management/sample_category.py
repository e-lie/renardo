from pathlib import Path
from typing import Dict, Optional, List, Tuple, Iterator

from .sample_file import SampleFile

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
