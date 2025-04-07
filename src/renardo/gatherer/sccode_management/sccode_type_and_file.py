

# class SCCodeFile:
#     """Represents a single SuperCollider synthdef file."""
#     def __init__(self, path: Path, synth_type: SCResourceType, category: str):
#         self.path = path
#         self.name = path.stem
#         self.extension = path.suffix
#         self.size = path.stat().st_size
#         self.type = synth_type
#         self.category = category

#     @property
#     def full_path(self) -> Path:
#         return self.path

#     def __str__(self) -> str:
#         return f"SynthDefFile({self.type.value}/{self.category}/{self.name})"

#     def __repr__(self) -> str:
#         return self.__str__()

