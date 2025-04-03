from pathlib import Path
from typing import Dict, Optional, List, Iterator

from renardo.gatherer.sccode_management.sccode_type_and_file import SCCodeFile, SCCodeType


class SCCodeCategory:
    """Represents a collection of synthdefs in a category (e.g., 'bass', 'lead' or 'reverb', 'delay')."""
    def __init__(self, directory: Path, category: str, synth_type: SCCodeType):
        self.directory = directory
        self.category = category
        self.type = synth_type
        self._synthdefs: Dict[str, SCCodeFile] = {}
        self._load_synthdefs()

    def _load_synthdefs(self):
        """Load all synthdef files from the category directory."""
        synthdef_extensions = {'.scsyndef'}  # SuperCollider compiled synthdef extension
        scd_extensions = {'.scd', '.sc'}     # SuperCollider source file extensions

        for file_path in self.directory.iterdir():
            if file_path.is_file():
                if file_path.suffix.lower() in synthdef_extensions:
                    synthdef = SCCodeFile(file_path, self.type, self.category)
                    self._synthdefs[synthdef.name] = synthdef
                elif file_path.suffix.lower() in scd_extensions:
                    synthdef = SCCodeFile(file_path, self.type, self.category)
                    self._synthdefs[synthdef.name] = synthdef


    def get_synthdef(self, name: str) -> Optional[SCCodeFile]:
        """Get a synthdef by its name."""
        return self._synthdefs.get(name)

    def list_synthdefs(self) -> List[str]:
        """List all synthdef names in this category."""
        return list(self._synthdefs.keys())

    def __len__(self) -> int:
        return len(self._synthdefs)

    def __iter__(self) -> Iterator[SCCodeFile]:
        return iter(self._synthdefs.values())

    def __str__(self) -> str:
        return f"SynthDefCategory({self.type.value}/{self.category}, {len(self)} synthdefs)"
