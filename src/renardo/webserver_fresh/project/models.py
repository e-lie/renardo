from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class FileInfo(BaseModel):
    """Information about a file in the project"""
    path: str
    name: str
    is_directory: bool
    size: Optional[int] = None
    extension: Optional[str] = None


class Project(BaseModel):
    """A code project with a root directory"""
    root_path: Path = Field(..., description="Root directory of the project")

    @field_validator('root_path', mode='before')
    @classmethod
    def validate_path(cls, v):
        """Validate and convert path to Path object"""
        if isinstance(v, str):
            v = Path(v)
        if not isinstance(v, Path):
            raise ValueError("root_path must be a Path or string")
        return v.resolve()

    class Config:
        arbitrary_types_allowed = True

    def exists(self) -> bool:
        """Check if project directory exists"""
        return self.root_path.exists() and self.root_path.is_dir()

    def list_files(self, pattern: str = "*", recursive: bool = False) -> list[FileInfo]:
        """
        List files in the project directory

        Args:
            pattern: Glob pattern to match files (default: "*")
            recursive: Whether to search recursively (default: False)

        Returns:
            List of FileInfo objects
        """
        if not self.exists():
            raise ValueError(f"Project directory does not exist: {self.root_path}")

        glob_method = self.root_path.rglob if recursive else self.root_path.glob
        files = []

        for path in glob_method(pattern):
            relative_path = path.relative_to(self.root_path)
            files.append(FileInfo(
                path=str(relative_path),
                name=path.name,
                is_directory=path.is_dir(),
                size=path.stat().st_size if path.is_file() else None,
                extension=path.suffix if path.is_file() else None
            ))

        return sorted(files, key=lambda f: (not f.is_directory, f.name))

    def read_file(self, file_path: str) -> str:
        """
        Read a text file from the project

        Args:
            file_path: Relative path to the file within the project

        Returns:
            File content as string
        """
        full_path = self.root_path / file_path

        # Security check: ensure file is within project directory
        if not str(full_path.resolve()).startswith(str(self.root_path.resolve())):
            raise ValueError(f"File path escapes project directory: {file_path}")

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not full_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        try:
            return full_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            raise ValueError(f"File is not a valid UTF-8 text file: {file_path}")

    def write_file(self, file_path: str, content: str) -> None:
        """
        Write content to a file in the project

        Args:
            file_path: Relative path to the file within the project
            content: Content to write to the file
        """
        full_path = self.root_path / file_path

        # Security check: ensure file is within project directory
        if not str(full_path.resolve()).startswith(str(self.root_path.resolve())):
            raise ValueError(f"File path escapes project directory: {file_path}")

        # Create parent directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)

        full_path.write_text(content, encoding='utf-8')

    def get_absolute_path(self, file_path: str) -> Path:
        """
        Get the absolute path for a file in the project

        Args:
            file_path: Relative path to the file within the project

        Returns:
            Absolute Path object
        """
        full_path = self.root_path / file_path

        # Security check: ensure file is within project directory
        if not str(full_path.resolve()).startswith(str(self.root_path.resolve())):
            raise ValueError(f"File path escapes project directory: {file_path}")

        return full_path.resolve()
