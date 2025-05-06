"""
RenardoApp - Main application class for Renardo
"""
import argparse
import time

from renardo.tui import write_sc_renardo_files_in_user_config
from renardo.tui import SupercolliderInstance
from renardo.tui import PulsarInstance
from renardo.webserver import run_webserver

from .state_manager import StateManager


class RenardoApp:
    """
    Main application class for Renardo
    """
    _instance = None  # Singleton instance
    
    @classmethod
    def get_instance(cls):
        """Get or create the singleton instance"""
        if cls._instance is None:
            cls._instance = RenardoApp()
        return cls._instance
    
    def __init__(self):
        """Initialize the Renardo application"""
        # Ensure only one instance is created
        if RenardoApp._instance is not None:
            raise RuntimeError("RenardoApp is a singleton class. Use RenardoApp.get_instance() instead.")
            
        # Create state manager
        self.state_manager = StateManager()
        
        # SuperCollider and Pulsar instances
        self.sc_instance = None
        self.pulsar_instance = None
        
        # Parse arguments
        self.args = self.parse_args()
        
        # Initialize components 
        self.sc_instance = SupercolliderInstance()
        self.pulsar_instance = PulsarInstance()
        
        # Set singleton instance
        RenardoApp._instance = self
    
    def launch(self):
        """Launch the Renardo application"""
        # Handle command-line options
        if self.args.create_scfiles:
            write_sc_renardo_files_in_user_config()
            
            # Update the state
            self.state_manager.update_renardo_init_status("superColliderClasses", True)

        # Launch web server if not using pipe or foxdot editor
        if not (self.args.pipe or self.args.foxdot_editor):
            run_webserver()

        # Handle different run modes
        if self.args.pipe:
            from renardo.lib.runtime import handle_stdin, FoxDotCode
            # Just take commands from the CLI
            handle_stdin()
        elif self.args.foxdot_editor:
            from renardo.lib.runtime import FoxDotCode
            # Open the GUI
            from renardo.foxdot_editor.Editor import workspace
            FoxDot = workspace(FoxDotCode).run()
        elif self.args.no_tui:
            print("You need to choose a launching mode: TUI, --pipe or --foxdot-editor...")
        
        print("Quitting...")

    @staticmethod
    def parse_args():
        """Parse command-line arguments"""
        parser = argparse.ArgumentParser(
            prog="renardo",
            description="Live coding with Python and SuperCollider",
            epilog="More information: https://renardo.org/"
        )
        parser.add_argument('-p', '--pipe', action='store_true', help="run Renardo from the command line interface")
        parser.add_argument('-f', '--foxdot-editor', action='store_true', help="run Renardo with the classic FoxDot code editor")
        parser.add_argument('-c', '--create-scfiles', action='store_true', help="Create Renardo class file and startup file in SuperCollider user conf dir.")
        parser.add_argument('-N', '--no-tui', action='store_true', help="Don't start Renardo TUI")

        return parser.parse_args()