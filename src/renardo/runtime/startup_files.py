import os
import sys
from pathlib import Path
from renardo.settings_manager import settings

class StartupFile:
    """ Manages loading of startup file code """
    def __init__(self, path=None):
        self.path = None
        if path is not None:
            self.set_path(path)
    
    def set_path(self, path):
        """ Set the path to the startup file """
        if path is None:
            self.path = None
        else:
            self.path = Path(path).resolve()
        return self

    def load(self):
        """ Load and return the content of the startup file """
        if self.path is not None:
            try:
                with open(self.path) as file:
                    code = file.read()
                return code
            except (IOError, OSError):
                print(f"Warning: '{self.path}' startup file not found.")
        return ""

def get_startup_file():
    """
    Get the current startup file path, using settings to determine which one to load
    """
    # Check if a specific startup file is specified in settings
    startup_file_name = settings.get("core.STARTUP_FILE_NAME", "startup.py")
    
    # Create a path to the user's startup_files directory
    user_dir = settings.get_renardo_user_dir()
    startup_files_dir = user_dir / "startup_files"
    
    # Create the directory if it doesn't exist
    startup_files_dir.mkdir(exist_ok=True, parents=True)
    
    # Check if the specified startup file exists in the user directory
    user_startup_file = startup_files_dir / startup_file_name
    
    if user_startup_file.exists():
        return user_startup_file
    
    # If not found in user dir, create an empty default file
    if startup_file_name == "startup.py":
        with open(user_startup_file, 'w') as f:
            f.write("# Renardo startup file\n")
            f.write("# This file is loaded when Renardo starts\n")
            f.write("# Add your custom code here\n")
        return user_startup_file
    
    # Otherwise use the built-in startup file path
    built_in_path = settings.get_path("RENARDO_ROOT_PATH") / "lib" / "Custom" / "startup.py"
    
    if built_in_path.exists():
        return built_in_path
    
    return None

def create_startup_directory():
    """
    Ensure the startup_files directory exists in the user directory.
    """
    user_dir = settings.get_renardo_user_dir()
    startup_files_dir = user_dir / "startup_files"
    
    # Create the directory if it doesn't exist
    startup_files_dir.mkdir(exist_ok=True, parents=True)
    
    # Create a default file if none exists
    default_file = startup_files_dir / "startup.py"
    
    if not default_file.exists():
        with open(default_file, 'w') as f:
            f.write("# Renardo startup file\n")
            f.write("# This file is loaded when Renardo starts\n")
            f.write("# Add your custom code here\n")
    
    return startup_files_dir

# Initialize the startup file
STARTUP_FILE = StartupFile(str(get_startup_file()))

def load_startup_file():
    """
    Load the content of the current startup file
    """
    return STARTUP_FILE.load()