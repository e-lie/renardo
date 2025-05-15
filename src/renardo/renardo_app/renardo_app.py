"""
RenardoApp - Main application class for Renardo
"""
import argparse
import time

from renardo.sc_backend import write_sc_renardo_files_in_user_config
from renardo.webserver import create_webapp
from renardo.webserver.config import HOST, PORT, DEBUG
from renardo.reaper_backend.reaper_mgt.launcher import (
    launch_reaper_with_pythonhome,
    initialize_reapy,
    reinit_reaper_with_backup
)

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
        
        # Flask webapp instance
        self.webapp = None
        
        # Parse arguments
        self.args = self.parse_args()
        
        # Set singleton instance
        RenardoApp._instance = self
    
    def launch(self):
        """Launch the Renardo application"""
        import os
        import threading
        import time
        import webbrowser
        
        # Handle command-line options
        if self.args.create_scfiles:
            write_sc_renardo_files_in_user_config()
            # Update the state
            self.state_manager.update_renardo_init_status("superColliderClasses", True)
        
        # REAPER integration options
        if self.args.launch_reaper:
            print("Launching REAPER with correct PYTHONHOME environment...")
            if launch_reaper_with_pythonhome():
                print("REAPER launched successfully")
            else:
                print("Failed to launch REAPER")
            return
                
        elif self.args.initialize_reapy:
            print("Starting Reapy initialization process...")
            success = initialize_reapy()
            if success:
                print("Reapy initialization completed successfully")
                # Update the state
                self.state_manager.update_renardo_init_status("reaperIntegration", True)
            else:
                print("Reapy initialization failed")
            return
                
        elif self.args.reinit_reaper:
            print("Backing up and reinitializing REAPER configuration...")
            if reinit_reaper_with_backup():
                print("REAPER configuration has been backed up and will be reset on next launch")
            else:
                print("Failed to backup and reinitialize REAPER configuration")
            return
                
        # Original reapy integration
        elif self.args.reapy:
            try:
                import reapy
                reapy.configure_reaper()
                print("Reaper integration enabled successfully")
                # Update the state
                self.state_manager.update_renardo_init_status("reaperIntegration", True)
            except ImportError:
                print("Error: reapy module not found. Please install it to use Reaper integration.")
            except Exception as e:
                print(f"Error configuring Reaper integration: {e}")
            return
        
        # Create and launch web server if not using pipe or foxdot editor
        if not (self.args.pipe or self.args.foxdot_editor):
            # Create the Flask application if it doesn't exist
            webapp = self.create_webapp_instance()
            
            # Define function to open browser after a short delay
            def open_browser_after_delay():
                # Wait for the server to start up
                time.sleep(1.5)
                # Determine the URL based on the host and port
                url = f"http://localhost:{PORT}" if HOST == "0.0.0.0" else f"http://{HOST}:{PORT}"
                print(f"Opening browser at {url}")
                webbrowser.open(url)
                
            # Start browser in a separate thread if not disabled
            if not self.args.no_browser:
                browser_thread = threading.Thread(target=open_browser_after_delay)
                browser_thread.daemon = True
                browser_thread.start()
            
            # Run the web server with Gunicorn or Flask development server
            if self.args.use_gunicorn:
                self._run_with_gunicorn()
            else:
                # Run the Flask application (development server)
                webapp.run(
                    host=HOST,
                    port=PORT,
                    debug=DEBUG
                )
        # Handle different run modes
        elif self.args.pipe:
            from renardo.runtime import handle_stdin, FoxDotCode
            # Just take commands from the CLI
            handle_stdin()
        elif self.args.foxdot_editor:
            from renardo.runtime import FoxDotCode
            # Open the GUI
            from renardo.foxdot_editor.Editor import workspace
            FoxDot = workspace(FoxDotCode).run()
        elif self.args.no_tui:
            print("You need to choose a launching mode: TUI, --pipe or --foxdot-editor...")
        
        print("Quitting...")
        
    def _run_with_gunicorn(self):
        """Run the web application with Gunicorn"""
        import subprocess
        import sys
        import os
        import importlib.util
        from pathlib import Path
        
        try:
            # Import gunicorn to verify it's installed
            import gunicorn
            import gevent
        except ImportError as e:
            print(f"Error: Missing dependency: {e}")
            print("Please install required packages with: pip install gunicorn gevent")
            sys.exit(1)
            
        # Get path to the webserver module
        from renardo import webserver
        webserver_path = Path(webserver.__file__).parent
        
        # Get the path to the gunicorn config
        gunicorn_config = webserver_path / "gunicorn_config.py"
        
        # Get the path to the WSGI module
        wsgi_module = "renardo.webserver.wsgi:app"
        
        print(f"Starting Gunicorn server at {HOST}:{PORT}...")
        
        # Instead of running Gunicorn as a separate process, we'll invoke it through its API
        # This avoids the command-line argument parsing issue
        try:
            # Import the necessary module
            from gunicorn.app.wsgiapp import WSGIApplication
            
            # Create a custom WSGI application class that loads our config
            class RenardoWSGIApplication(WSGIApplication):
                def __init__(self, config_path):
                    self.config_path = config_path
                    super().__init__()
                
                def load_config(self):
                    # Load the config file first
                    config_path = self.config_path
                    
                    # Check if file exists
                    if not os.path.exists(config_path):
                        print(f"Error: Config file not found: {config_path}")
                        sys.exit(1)
                    
                    # Load the module
                    spec = importlib.util.spec_from_file_location("gunicorn_config", config_path)
                    config_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(config_module)
                    
                    # Load settings from the module
                    for key in dir(config_module):
                        if key.isupper():
                            continue
                            
                        # Skip internal attributes and functions
                        if key.startswith('__'):
                            continue
                            
                        value = getattr(config_module, key)
                        if callable(value) or value is None:
                            continue
                            
                        self.cfg.set(key, value)
                    
                    # Add our application module
                    self.app_uri = wsgi_module
            
            # Initialize and run the Gunicorn application
            gunicorn_app = RenardoWSGIApplication(str(gunicorn_config))
            gunicorn_app.run()
            
        except Exception as e:
            print(f"Error starting Gunicorn: {e}")
            # Fallback to subprocess method if the direct invocation fails
            print("Falling back to subprocess method...")
            
            # Use Python to explicitly run the process to avoid argument parsing issues
            python_executable = sys.executable
            cmd = [
                python_executable,
                "-m", "gunicorn.app.wsgiapp",
                "--config", str(gunicorn_config),
                wsgi_module
            ]
            
            # Run gunicorn
            process = subprocess.Popen(cmd)
            
            try:
                # Wait for gunicorn to exit
                process.wait()
            except KeyboardInterrupt:
                print("\nShutting down Gunicorn...")
                process.terminate()
                process.wait()

    def create_webapp_instance(self):
        """
        Create the Flask webapp instance if it doesn't exist
        
        Returns:
            Flask: The Flask webapp instance
        """
        if self.webapp is None:
            self.webapp = create_webapp()
        return self.webapp
        
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
        parser.add_argument('-g', '--use-gunicorn', action='store_true', help="Use Gunicorn to serve the web application (1 process, 10 threads)")
        parser.add_argument('--no-browser', action='store_true', help="Don't automatically open the web browser when starting the server")
        
        # REAPER integration arguments
        reaper_group = parser.add_argument_group('REAPER Integration')
        reaper_group.add_argument('-r', '--reapy', action='store_true', help="Enable REAPER integration with Reapy")
        reaper_group.add_argument('--launch-reaper', action='store_true', help="Launch REAPER with correct PYTHONHOME environment")
        reaper_group.add_argument('--initialize-reapy', action='store_true', help="Run interactive Reapy initialization process")
        reaper_group.add_argument('--reinit-reaper', action='store_true', help="Backup current REAPER config and reset to default")

        return parser.parse_args()