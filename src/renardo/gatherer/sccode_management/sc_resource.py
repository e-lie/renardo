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
    
    def get_code_with_args(self, **kwargs) -> str:
        """
        Return the SuperCollider code with the specified arguments.
        Any arguments not specified will use their default values from self.arguments.
        """
        # Create a dictionary with default arguments
        args = self.arguments.copy()
        
        # Update with any provided arguments
        args.update(kwargs)
        
        # Get the function signature part of the SynthDef
        import re
        match = re.search(r'SynthDef\s*\(\s*["\']([^"\']+)["\']?\s*,\s*\{\s*\|([^|]*)\|', self.code)
        if not match:
            return self.code  # Return original code if no match found
            
        # Extract the synth name and argument string
        synth_name, arg_string = match.groups()
        
        # Build new argument string with updated values
        new_arg_parts = []
        for arg_def in arg_string.split(','):
            arg_def = arg_def.strip()
            if '=' in arg_def:
                arg_name, _ = arg_def.split('=', 1)
                arg_name = arg_name.strip()
                if arg_name in args:
                    new_arg_parts.append(f"{arg_name}={args[arg_name]}")
                else:
                    new_arg_parts.append(arg_def)
            else:
                new_arg_parts.append(arg_def)
        
        new_arg_string = ', '.join(new_arg_parts)
        
        # Replace the old argument string with the new one
        new_code = re.sub(
            r'(SynthDef\s*\(\s*["\']' + re.escape(synth_name) + r'["\']?\s*,\s*\{\s*\|)([^|]*)(\|)',
            r'\1' + new_arg_string + r'\3',
            self.code
        )
        
        return new_code
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.shortname}, {len(self.arguments)} args)"
    
    def __repr__(self) -> str:
        return self.__str__()


class SCSynth(SCResource):
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