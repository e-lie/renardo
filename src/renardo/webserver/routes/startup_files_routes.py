"""
Startup Files API route handlers
"""
import os
from pathlib import Path
from flask import jsonify, request
from renardo.settings_manager import settings
import subprocess
import platform
from renardo.gatherer.reaper_resource_management.default_reaper_pack import is_default_reaper_pack_initialized, download_reaper_pack

def register_startup_files_routes(webapp):
    """
    Register Startup Files API routes with the Flask application
    
    Args:
        webapp: Flask application instance
    """
    @webapp.route('/api/settings/user-directory/startup_files', methods=['GET'])
    def list_startup_files():
        """
        List available startup files
        
        Returns:
            JSON: List of startup files
        """
        try:
            # Get startup files directory
            user_dir = settings.get_renardo_user_dir()
            startup_files_dir = user_dir / "startup_files"
            
            # Create directory if it doesn't exist
            startup_files_dir.mkdir(exist_ok=True, parents=True)
            
            # Check which file is currently set as default
            current_default = settings.get("core.STARTUP_FILE_NAME", "default.py")
            
            # List all .py files in startup_files directory
            files = []
            for file_path in sorted(startup_files_dir.glob("*.py")):
                files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "url": f"/api/settings/user-directory/startup_files/{file_path.name}",
                    "is_default": file_path.name == current_default
                })
                
            return jsonify({
                "success": True,
                "files": files,
                "default_file": current_default
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error listing startup files: {str(e)}"
            }), 500
            
    @webapp.route('/api/settings/user-directory/startup_files/<filename>', methods=['GET'])
    def get_startup_file(filename):
        """
        Get a specific startup file
        
        Args:
            filename (str): Name of the startup file
            
        Returns:
            JSON: Startup file content
        """
        try:
            user_dir = settings.get_renardo_user_dir()
            startup_files_dir = user_dir / "startup_files"
            file_path = startup_files_dir / filename
            
            # Security check - ensure the file is within the startup_files directory
            if not file_path.resolve().is_relative_to(startup_files_dir.resolve()):
                return jsonify({
                    "success": False,
                    "message": "Access denied"
                }), 403
                
            # Check if file exists
            if not file_path.exists():
                return jsonify({
                    "success": False,
                    "message": "Startup file not found"
                }), 404
                
            # Read and return the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return jsonify({
                "success": True,
                "filename": filename,
                "content": content
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error loading startup file: {str(e)}"
            }), 500
            
    @webapp.route('/api/settings/user-directory/startup_files/save', methods=['POST'])
    def save_startup_file():
        """
        Save a startup file
        
        Request body:
            {
                "path": "/path/to/startup_files/file.py",
                "content": "code content"
            }
            
        Returns:
            JSON: Save status
        """
        try:
            data = request.get_json()
            
            if not data or 'path' not in data or 'content' not in data:
                return jsonify({
                    "success": False,
                    "message": "Missing 'path' or 'content' in request data"
                }), 400
                
            file_path = Path(data['path'])
            content = data['content']
            
            # Get startup files directory
            user_dir = settings.get_renardo_user_dir()
            startup_files_dir = user_dir / "startup_files"
            
            # Security check - ensure the file is within the startup_files directory
            if not file_path.resolve().is_relative_to(startup_files_dir.resolve()):
                return jsonify({
                    "success": False,
                    "message": "Access denied - path must be within startup_files directory"
                }), 403
                
            # Save the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return jsonify({
                "success": True,
                "message": f"Startup file saved",
                "path": str(file_path)
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error saving startup file: {str(e)}"
            }), 500
            
    @webapp.route('/api/settings/user-directory/startup_files/create', methods=['POST'])
    def create_startup_file():
        """
        Create a new startup file
        
        Request body:
            {
                "filename": "my_startup.py",
                "content": "# Startup code here"
            }
            
        Returns:
            JSON: Creation status
        """
        try:
            data = request.get_json()
            
            if not data or 'filename' not in data:
                return jsonify({
                    "success": False,
                    "message": "Missing 'filename' in request data"
                }), 400
                
            filename = data['filename']
            content = data.get('content', '')
            
            # Ensure filename ends with .py
            if not filename.endswith('.py'):
                filename += '.py'
                
            # Get startup files directory
            user_dir = settings.get_renardo_user_dir()
            startup_files_dir = user_dir / "startup_files"
            
            # Create directory if it doesn't exist
            startup_files_dir.mkdir(exist_ok=True, parents=True)
            
            # Create the file
            file_path = startup_files_dir / filename
            
            # Check if file already exists
            if file_path.exists():
                return jsonify({
                    "success": False,
                    "message": f"File '{filename}' already exists"
                }), 400
                
            # Create the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return jsonify({
                "success": True,
                "message": f"Startup file '{filename}' created",
                "filename": filename,
                "path": str(file_path),
                "url": f"/api/settings/user-directory/startup_files/{filename}"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error creating startup file: {str(e)}"
            }), 500
            
    @webapp.route('/api/settings/user-directory/startup_files/open', methods=['POST'])
    def open_startup_files_directory():
        """
        Open the startup_files directory in the OS file browser
        
        Returns:
            JSON: Operation status
        """
        try:
            # Get startup files directory
            user_dir = settings.get_renardo_user_dir()
            startup_files_dir = user_dir / "startup_files"
            
            # Create directory if it doesn't exist
            startup_files_dir.mkdir(exist_ok=True, parents=True)
            
            # Platform-specific commands to open directory
            if platform.system() == 'Windows':
                subprocess.Popen(['explorer', str(startup_files_dir)])
            elif platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['open', str(startup_files_dir)])
            else:  # Linux and others
                subprocess.Popen(['xdg-open', str(startup_files_dir)])
                
            return jsonify({
                "success": True,
                "message": "Startup files directory opened"
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error opening startup files directory: {str(e)}"
            }), 500
    
    @webapp.route('/api/settings/startup_files/set_default', methods=['POST'])
    def set_default_startup_file():
        """
        Set a startup file as the default one to be loaded on startup
        
        Request body:
            {
                "filename": "my_startup.py"
            }
            
        Returns:
            JSON: Update status
        """
        try:
            data = request.get_json()
            
            if not data or 'filename' not in data:
                return jsonify({
                    "success": False,
                    "message": "Missing 'filename' in request data"
                }), 400
                
            filename = data['filename']
            
            # Ensure file exists
            user_dir = settings.get_renardo_user_dir()
            startup_files_dir = user_dir / "startup_files"
            file_path = startup_files_dir / filename
            
            if not file_path.exists():
                return jsonify({
                    "success": False,
                    "message": f"Startup file not found: {filename}"
                }), 404
            
            # Update the setting
            settings.set("core.STARTUP_FILE_NAME", filename, internal=False)
            
            # Save settings to file
            settings.save_to_file(save_internal=False)
            
            # Broadcast setting change to WebSocket clients
            from renardo.webserver import websocket_utils
            websocket_utils.broadcast_to_clients({
                "type": "setting_updated",
                "data": {
                    "key": "core.STARTUP_FILE_NAME",
                    "value": filename
                }
            })
            
            return jsonify({
                "success": True,
                "filename": filename,
                "message": "Default startup file updated successfully"
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error setting default startup file: {str(e)}"
            }), 500
            
    @webapp.route('/api/reaper/initialize_default_pack', methods=['POST'])
    def initialize_default_reaper_pack():
        """
        Initialize the default Reaper resource pack if not already initialized
        
        Returns:
            JSON: Initialization status
        """
        try:
            # Get the default reaper pack name from settings
            default_pack_name = settings.get("reaper_backend.DEFAULT_REAPER_PACK_NAME", "0_renardo_core")
            
            # Check if already initialized
            if is_default_reaper_pack_initialized():
                return jsonify({
                    "success": True,
                    "message": f"Default Reaper resource pack '{default_pack_name}' is already initialized",
                    "already_initialized": True
                })
            
            # Initialize the pack
            download_success = download_reaper_pack(default_pack_name)
            
            if download_success:
                return jsonify({
                    "success": True,
                    "message": f"Successfully initialized default Reaper resource pack: {default_pack_name}"
                })
            else:
                return jsonify({
                    "success": False,
                    "message": f"Failed to initialize default Reaper resource pack: {default_pack_name}"
                }), 500
                
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error initializing default Reaper resource pack: {str(e)}"
            }), 500