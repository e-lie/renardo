from pathlib import Path


class SampleFile:
    """Represents a single audio sample file with an index."""
    def __init__(self, path: Path, category: str, index: int):
        self.path = path
        self.name = path.stem
        self.extension = path.suffix
        self.size = path.stat().st_size
        self.category = category  # The letter/symbol/keyword category
        self.index = index  # The numerical index

    @property
    def full_path(self) -> Path:
        return self.path

    def __str__(self) -> str:
        return f"SampleFile({self.category}{self.index}: {self.name}{self.extension})"

    def __repr__(self) -> str:
        return self.__str__()
