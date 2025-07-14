"""Core REAPER functionality module."""

import logging
import os
from pathlib import Path
from typing import Optional, List, Union, Dict, Any

logger = logging.getLogger(__name__)

class Reaper:
    """Main interface to REAPER."""
    
    def __init__(self, client):
        """Initialize the Reaper object.
        
        Parameters
        ----------
        client : ReaperClient
            Client for communicating with REAPER.
        """
        self._client = client
        self._projects = {}  # Cache for Project objects
        
    @property
    def version(self) -> str:
        """Get REAPER version.
        
        Returns
        -------
        str
            REAPER version string.
        """
        return self._client.get_reaper_version()
    
    @property
    def position(self) -> float:
        """Get current cursor position in seconds.
        
        Returns
        -------
        float
            Current cursor position in seconds.
        """
        return self._client.get_time_position()
    
    @position.setter
    def position(self, pos: float) -> None:
        """Set current cursor position.
        
        Parameters
        ----------
        pos : float
            Position in seconds.
        """
        self._client.goto_time(pos)
    
    @property
    def is_playing(self) -> bool:
        """Check if REAPER is currently playing.
        
        Returns
        -------
        bool
            True if REAPER is playing.
        """
        play_state = self._client.get_play_state()
        return play_state == 1
    
    @property
    def is_recording(self) -> bool:
        """Check if REAPER is currently recording.
        
        Returns
        -------
        bool
            True if REAPER is recording.
        """
        play_state = self._client.get_play_state()
        return play_state == 5
    
    @property
    def is_stopped(self) -> bool:
        """Check if REAPER is currently stopped.
        
        Returns
        -------
        bool
            True if REAPER is stopped.
        """
        return not self.is_playing and not self.is_recording
    
    def play(self) -> None:
        """Start playback."""
        self._client.play()
    
    def stop(self) -> None:
        """Stop playback."""
        self._client.stop()
    
    def pause(self) -> None:
        """Pause playback."""
        self._client.pause()
    
    def record(self) -> None:
        """Start recording."""
        self._client.record()
    
    def perform_action(self, action_id: Union[int, str]) -> bool:
        """Perform a REAPER action by ID.
        
        Parameters
        ----------
        action_id : int or str
            Action ID to perform.
            
        Returns
        -------
        bool
            True if action was performed successfully.
        """
        return self._client.perform_action(action_id)
    
    @property
    def current_project(self):
        """Get current project.
        
        Returns
        -------
        Project
            Current project object.
        """
        from .project import Project
        
        # Get current project index - use EnumProjects to check the active project
        try:
            # REAPER doesn't have a CountProjects function, so we implement our own
            # method to determine the current project
            
            # Default to the first project (index 0)
            project_index = 0
            
            # Try to get the current project using EnumProjects with -1 (gets current project)
            try:
                self._client.call_reascript_function("EnumProjects", -1, "")
                # If successful, current project is at index 0
            except:
                # If that fails, just use index 0
                pass
                
        except:
            # Fallback to index 0 if there's an error
            project_index = 0
        
        # Check cache and create Project object if needed
        if project_index not in self._projects:
            self._projects[project_index] = Project(self, project_index)
            
        return self._projects[project_index]
    
    def get_project(self, index: int):
        """Get project by index.
        
        Parameters
        ----------
        index : int
            Project index.
            
        Returns
        -------
        Project
            Project object.
            
        Raises
        ------
        ValueError
            If project with specified index doesn't exist.
        """
        from .project import Project
        
        # Check if project exists
        try:
            # Try to access the project directly using EnumProjects
            # If the project doesn't exist, this will raise an exception
            proj = self._client.call_reascript_function("EnumProjects", index, "")
            if not proj:
                raise ValueError(f"Project at index {index} doesn't exist")
        except Exception as e:
            raise ValueError(f"Error checking project: {str(e)}")
        
        # Check cache and create Project object if needed
        if index not in self._projects:
            self._projects[index] = Project(self, index)
            
        return self._projects[index]
    
    @property
    def projects(self) -> List:
        """Get list of all projects.
        
        Returns
        -------
        list of Project
            List of all open projects.
        """
        from .project import Project
        
        projects = []
        
        try:
            # Since there's no CountProjects function, we need to enumerate projects
            # until we get an error or empty result
            index = 0
            while True:
                try:
                    proj = self._client.call_reascript_function("EnumProjects", index, "")
                    if not proj:
                        # We've reached the end of projects
                        break
                        
                    # Project exists, add it to our list
                    if index not in self._projects:
                        self._projects[index] = Project(self, index)
                    
                    projects.append(self._projects[index])
                    index += 1
                except Exception:
                    # If there's an error, we've likely reached the end of projects
                    break
        except Exception as e:
            # If there's an unexpected error, just return what we have so far
            pass
                
        return projects
    
    def add_project(self) -> 'Project':
        """Add a new project tab.
        
        Returns
        -------
        Project
            New project object.
        """
        from .project import Project
        
        # Create new project tab (Action ID: 40859)
        self._client.perform_action(40859)
        
        # Get the new project
        return self.current_project
        
    def available_fxchains(self, custom_dir: Optional[Union[str, Path]] = None, 
                        include_subdirs: bool = True, 
                        search_pattern: Optional[str] = None) -> Dict[str, Path]:
        """Get available FX chains in REAPER.
        
        Parameters
        ----------
        custom_dir : str or Path, optional
            Custom directory to search for FX chains. If None, searches in REAPER's 
            default FX chains directory.
        include_subdirs : bool, optional
            Whether to include subdirectories in the search. Default is True.
        search_pattern : str, optional
            Pattern to filter FX chains by name. Case-insensitive partial matching.
            
        Returns
        -------
        Dict[str, Path]
            Dictionary mapping FX chain names to their file paths. 
            Keys format depends on location:
            - For top-level files: "filename"
            - For subdirectory files: "subdirname/filename"
        """
        fx_chains = {}
        
        # Search in REAPER's default FX chains directory
        default_dirs = self._get_reaper_fx_chain_directories()
        
        # Add custom directory if specified
        search_dirs = list(default_dirs)
        if custom_dir is not None:
            if isinstance(custom_dir, str):
                custom_dir = Path(custom_dir)
            if custom_dir.exists() and custom_dir.is_dir():
                search_dirs.append(custom_dir)
        
        # Log the directories being searched
        logger.debug(f"Searching for FX chains in: {[str(d) for d in search_dirs]}")
        
        # Search for FX chains in all directories
        for directory in search_dirs:
            if directory.exists() and directory.is_dir():
                # Use recursive glob if include_subdirs is True
                glob_pattern = "**/*.RfxChain" if include_subdirs else "*.RfxChain"
                for file_path in directory.glob(glob_pattern):
                    # For subdirectories, use relative path as part of the key to avoid name collisions
                    if include_subdirs and file_path.parent != directory:
                        # Create a key that includes the subdirectory structure
                        relative_path = file_path.relative_to(directory)
                        # Use the parent folder and filename as the key
                        key = f"{relative_path.parent.name}/{file_path.stem}"
                    else:
                        key = file_path.stem
                    
                    # Apply search pattern filter if provided
                    if search_pattern is None or search_pattern.lower() in key.lower():
                        fx_chains[key] = file_path
        
        logger.debug(f"Found {len(fx_chains)} FX chains")
        return fx_chains
        
    def find_fxchain(self, name: str, exact_match: bool = False) -> Optional[Path]:
        """Find an FX chain by name.
        
        Parameters
        ----------
        name : str
            Name of the FX chain to find.
        exact_match : bool, optional
            If True, requires an exact match. If False, uses partial matching.
            Default is False.
            
        Returns
        -------
        Path or None
            Path to the FX chain file if found, None otherwise.
        """
        chains = self.available_fxchains(include_subdirs=True)
        
        # Case for exact match
        if exact_match:
            if name in chains:
                return chains[name]
            
            # Also check for name with subdirectory
            for key, path in chains.items():
                if key.endswith(f"/{name}"):
                    return path
            return None
        
        # Case for partial match
        matches = {key: path for key, path in chains.items() 
                  if name.lower() in key.lower()}
        
        if matches:
            # Return the first match
            return next(iter(matches.values()))
            
        return None
    
    def _get_reaper_fx_chain_directories(self) -> List[Path]:
        """Get REAPER's FX chain directories.
        
        Returns
        -------
        List[Path]
            List of FX chain directory paths.
        """
        directories = []
        
        # Get REAPER resource path
        resource_path = self._get_reaper_resource_path()
        
        if resource_path:
            # REAPER's default FX chains directory
            fx_chains_dir = resource_path / "FXChains"
            if fx_chains_dir.exists() and fx_chains_dir.is_dir():
                directories.append(fx_chains_dir)
                
                # Check for renardo_fxchains subdirectory
                renardo_fxchains_dir = fx_chains_dir / "renardo_fxchains"
                if renardo_fxchains_dir.exists() and renardo_fxchains_dir.is_dir():
                    directories.append(renardo_fxchains_dir)
            
            # User's FX chains directory
            user_fx_chains_dir = resource_path / "UserPlugins" / "FXChains"
            if user_fx_chains_dir.exists() and user_fx_chains_dir.is_dir():
                directories.append(user_fx_chains_dir)
        
        # Try to get a custom path from REAPER config
        custom_path = self._client.call_reascript_function("GetExtState", "REAPER", "FXCHAIN_PATH")
        if custom_path:
            custom_dir = Path(custom_path)
            if custom_dir.exists() and custom_dir.is_dir():
                directories.append(custom_dir)
                
        # Check if RENARDO_FXCHAIN_DIR is stored as ExtState
        renardo_path = self._client.call_reascript_function("GetExtState", "REAPER", "RENARDO_FXCHAIN_DIR")
        if renardo_path:
            renardo_dir = Path(renardo_path)
            if renardo_dir.exists() and renardo_dir.is_dir():
                directories.append(renardo_dir)
                
        # Additional specific paths to check based on common Renardo setups
        if resource_path:
            # Check for a Renardo folder in REAPER config
            renardo_config_dir = resource_path / "Scripts" / "Renardo" / "FXChains"
            if renardo_config_dir.exists() and renardo_config_dir.is_dir():
                directories.append(renardo_config_dir)
                
        # Check for home directory ~/.config/renardo/fxchains
        home_dir = Path.home()
        if home_dir:
            renardo_home_dir = home_dir / ".config" / "renardo" / "fxchains"
            if renardo_home_dir.exists() and renardo_home_dir.is_dir():
                directories.append(renardo_home_dir)
        
        return directories
    
    def _get_reaper_resource_path(self) -> Optional[Path]:
        """Get REAPER's resource path.
        
        Returns
        -------
        Path or None
            Path to REAPER's resource directory, or None if it cannot be determined.
        """
        # Try to get the resource path from REAPER
        resource_path_str = self._client.call_reascript_function("GetResourcePath")
        
        if resource_path_str:
            return Path(resource_path_str)
        
        # Fallback for different OS platforms
        if os.name == 'nt':  # Windows
            appdata = os.getenv('APPDATA')
            if appdata:
                return Path(appdata) / 'REAPER'
        elif os.name == 'posix':  # macOS/Linux
            if os.uname().sysname == 'Darwin':  # macOS
                return Path('~/Library/Application Support/REAPER').expanduser()
            else:  # Linux
                return Path('~/.config/REAPER').expanduser()
                
        return None