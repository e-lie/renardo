from pathlib import Path
from typing import List
from .models import DirectoryEntry


class FileExplorerService:
    """Service for exploring the file system"""

    @staticmethod
    def list_directory(path: str) -> List[DirectoryEntry]:
        """
        List all entries in a directory

        Args:
            path: Path to the directory to list

        Returns:
            List of DirectoryEntry objects
        """
        directory = Path(path).resolve()

        if not directory.exists():
            raise ValueError(f"Directory does not exist: {path}")

        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {path}")

        entries = []

        try:
            for item in sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                try:
                    stat = item.stat()

                    # Check if directory has children
                    has_children = False
                    if item.is_dir():
                        try:
                            has_children = any(item.iterdir())
                        except PermissionError:
                            pass

                    entry = DirectoryEntry(
                        name=item.name,
                        path=str(item),
                        is_directory=item.is_dir(),
                        size=stat.st_size if item.is_file() else None,
                        modified_time=stat.st_mtime,
                        has_children=has_children
                    )
                    entries.append(entry)
                except (PermissionError, OSError):
                    # Skip entries we can't access
                    continue

        except PermissionError:
            raise ValueError(f"Permission denied to read directory: {path}")

        return entries

    @staticmethod
    def get_parent_directory(path: str) -> str:
        """Get the parent directory of a path"""
        parent = Path(path).resolve().parent
        return str(parent)

    @staticmethod
    def get_home_directory() -> str:
        """Get the user's home directory"""
        return str(Path.home())


# Singleton instance
file_explorer_service = FileExplorerService()
