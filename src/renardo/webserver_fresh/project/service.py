from pathlib import Path
from typing import Optional
from .models import Project, FileInfo


class ProjectService:
    """Service for managing projects"""

    def __init__(self):
        self._current_project: Optional[Project] = None

    @property
    def current_project(self) -> Optional[Project]:
        """Get the current active project"""
        return self._current_project

    def open_project(self, root_path: str | Path) -> Project:
        """
        Open a project from a directory path

        Args:
            root_path: Path to the project root directory

        Returns:
            Project object
        """
        project = Project(root_path=root_path)

        if not project.exists():
            raise ValueError(f"Project directory does not exist: {project.root_path}")

        self._current_project = project
        return project

    def close_project(self) -> None:
        """Close the current project"""
        self._current_project = None

    def list_files(self, pattern: str = "*", recursive: bool = False) -> list[FileInfo]:
        """
        List files in the current project

        Args:
            pattern: Glob pattern to match files
            recursive: Whether to search recursively

        Returns:
            List of FileInfo objects
        """
        if not self._current_project:
            raise ValueError("No project is currently open")

        return self._current_project.list_files(pattern, recursive)

    def read_file(self, file_path: str) -> str:
        """
        Read a file from the current project

        Args:
            file_path: Relative path to the file

        Returns:
            File content
        """
        if not self._current_project:
            raise ValueError("No project is currently open")

        return self._current_project.read_file(file_path)

    def write_file(self, file_path: str, content: str) -> None:
        """
        Write a file to the current project

        Args:
            file_path: Relative path to the file
            content: Content to write
        """
        if not self._current_project:
            raise ValueError("No project is currently open")

        self._current_project.write_file(file_path, content)


# Singleton instance
project_service = ProjectService()
