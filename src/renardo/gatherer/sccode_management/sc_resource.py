from typing import Dict, Any





class SCResource:
    """Base class for SuperCollider resources (synths and effects)."""
    
    def __init__(
        self,
        shortname: str,
        fullname: str,
        description: str,
        code: str,
        arguments: Dict[str, Any] = None
    ):
        self.shortname = shortname
        self.fullname = fullname
        self.description = description
        self.code = code  # SuperCollider language code as a multiline string
        self.arguments = arguments or {}
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.shortname}, {len(self.arguments)} args)"
    
    def __repr__(self) -> str:
        return self.__str__()


class SCInstrument(SCResource):
    """Represents a SuperCollider synthesizer instrument."""
    
    def __init__(
        self,
        shortname: str,
        fullname: str,
        description: str,
        code: str,
        arguments: Dict[str, Any] = None,
        category: str = None
    ):
        super().__init__(shortname, fullname, description, code, arguments)
        self.category = category
    
    def __str__(self) -> str:
        return f"SCSynth({self.shortname}, {len(self.arguments)} args)"


class SCEffect(SCResource):
    """Represents a SuperCollider effect processor."""
    
    def __init__(
        self,
        shortname: str,
        fullname: str,
        description: str,
        code: str,
        arguments: Dict[str, Any] = None,
        category: str = None
    ):
        super().__init__(shortname, fullname, description, code, arguments)
        self.category = category
    
    def __str__(self) -> str:
        return f"SCEffect({self.shortname}, {len(self.arguments)} args)"