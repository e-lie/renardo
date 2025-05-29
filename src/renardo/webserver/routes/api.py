"""
REST API route handlers
"""
from flask import jsonify, request
from renardo.webserver import state_helper
from renardo.webserver import websocket_utils
from renardo.settings_manager import settings
import json
import subprocess
import platform
import shutil
import tomli
import tomli_w

def register_api_routes(webapp):
    import requests
    import json
    """
    Register REST API routes with the Flask application
    
    Args:
        webapp: Flask application instance
    """
    @webapp.route('/api/state', methods=['GET'])
    def get_state():
        """
        Get current state
        
        Returns:
            JSON: Current state
        """
        return jsonify(state_helper.get_state())

    @webapp.route('/api/increment', methods=['POST'])
    def increment_counter():
        """
        Increment counter
        
        Returns:
            JSON: Updated state
        """
        state_helper.increment_counter()
        state = state_helper.get_state()
        
        # Broadcast to WebSocket clients
        websocket_utils.broadcast_to_clients({
            "type": "state_updated",
            "data": state
        })
        
        return jsonify(state)
    
    @webapp.route('/api/stats', methods=['GET'])
    def get_stats():
        """
        Get server statistics
        
        Returns:
            JSON: Server statistics
        """
        return jsonify({
            "active_connections": websocket_utils.get_active_connection_count(),
            "counter_value": state_helper.get_state()["counter"]
        })
    
    @webapp.route('/api/collections', methods=['GET'])
    def get_collections():
        """
        Get information about available collections
        
        Returns:
            JSON: Collections information
        """
        try:
            from renardo.gatherer.collection_info import get_all_collections_info
            collections_info = get_all_collections_info()
            return jsonify(collections_info)
        except Exception as e:
            return jsonify({
                "error": f"Error fetching collections: {str(e)}",
                "collections_server": settings.get("core.COLLECTIONS_DOWNLOAD_SERVER")
            }), 500
    
    # Simple logger class for collections API
    class CollectionLogger:
        def __init__(self, collection_type, collection_name):
            self.collection_type = collection_type
            self.collection_name = collection_name
            
        def write_line(self, message, level="INFO"):
            # Add log message to state service
            log_entry = state_helper.add_log_message(message, level)
            
            # Print to console as well
            print(f"[{level}] {message}")
            
            # Broadcast to WebSocket clients
            websocket_utils.broadcast_to_clients({
                "type": "log_message",
                "data": log_entry
            })
            
        def write_error(self, message):
            self.write_line(message, "ERROR")
    
    @webapp.route('/api/collections/<collection_type>/<collection_name>/download', methods=['POST'])
    def download_collection(collection_type, collection_name):
        """
        Download a specific collection
        
        Args:
            collection_type (str): Type of collection ('samples', 'sccode', or 'reaper')
            collection_name (str): Name of the collection
            
        Returns:
            JSON: Download status
        """
        # Create a logger for this download
        logger = CollectionLogger(collection_type, collection_name)
        
        try:
            if collection_type == 'samples':
                from renardo.gatherer.sample_management.default_samples import download_sample_pack, is_sample_pack_initialized
                
                # Check if already installed
                if is_sample_pack_initialized(collection_name):
                    logger.write_line(f"Sample pack '{collection_name}' is already installed", "WARN")
                    return jsonify({
                        "success": True,
                        "message": f"Sample pack '{collection_name}' is already installed",
                        "already_installed": True
                    })
                
                # Start download in a separate thread to avoid blocking
                def download_task():
                    try:
                        logger.write_line(f"🚀 STARTING DOWNLOAD: Sample pack '{collection_name}'...", "INFO")
                        logger.write_line(f"Please wait while we prepare and download the files...", "INFO")
                        success = download_sample_pack(collection_name, logger)
                        
                        if success:
                            logger.write_line(f"🎉 DOWNLOAD SUCCESSFUL: Sample pack '{collection_name}' has been installed!", "SUCCESS")
                            logger.write_line(f"You can now use these samples in your compositions.", "SUCCESS")
                            
                            # Broadcast updated status to all WebSocket clients
                            websocket_utils.broadcast_to_clients({
                                "type": "collection_downloaded",
                                "data": {
                                    "type": "samples",
                                    "name": collection_name,
                                    "success": True
                                }
                            })
                        else:
                            logger.write_error(f"❌ DOWNLOAD FAILED: Sample pack '{collection_name}' could not be installed completely.")
                            logger.write_error(f"Please try again later or contact support if the issue persists.")
                    except Exception as e:
                        logger.write_error(f"❌ ERROR DURING DOWNLOAD: Sample pack '{collection_name}': {str(e)}")
                        logger.write_error(f"Please try again later or check your network connection.")
                
                # Start download thread
                import threading
                thread = threading.Thread(target=download_task)
                thread.daemon = True
                thread.start()
                
                return jsonify({
                    "success": True,
                    "message": f"Download of sample pack '{collection_name}' started",
                    "in_progress": True
                })
                    
            elif collection_type == 'sccode':
                from renardo.gatherer.sccode_management.default_sccode_pack import download_sccode_pack, is_sccode_pack_initialized
                
                # Check if already installed
                if is_sccode_pack_initialized(collection_name):
                    logger.write_line(f"SuperCollider code pack '{collection_name}' is already installed", "WARN")
                    return jsonify({
                        "success": True,
                        "message": f"SuperCollider code pack '{collection_name}' is already installed",
                        "already_installed": True
                    })
                
                # Start download in a separate thread to avoid blocking
                def download_task():
                    try:
                        logger.write_line(f"🚀 STARTING DOWNLOAD: SuperCollider code pack '{collection_name}'...", "INFO")
                        logger.write_line(f"Please wait while we prepare and download the instruments and effects...", "INFO")
                        success = download_sccode_pack(collection_name, logger)
                        
                        if success:
                            logger.write_line(f"🎉 DOWNLOAD SUCCESSFUL: SuperCollider code pack '{collection_name}' has been installed!", "SUCCESS")
                            logger.write_line(f"You can now use these instruments and effects in your compositions.", "SUCCESS")
                            
                            # Broadcast updated status to all WebSocket clients
                            websocket_utils.broadcast_to_clients({
                                "type": "collection_downloaded",
                                "data": {
                                    "type": "sccode",
                                    "name": collection_name,
                                    "success": True
                                }
                            })
                        else:
                            logger.write_error(f"❌ DOWNLOAD FAILED: SuperCollider code pack '{collection_name}' could not be installed completely.")
                            logger.write_error(f"Please try again later or contact support if the issue persists.")
                    except Exception as e:
                        logger.write_error(f"❌ ERROR DURING DOWNLOAD: SuperCollider code pack '{collection_name}': {str(e)}")
                        logger.write_error(f"Please try again later or check your network connection.")
                
                # Start download thread
                import threading
                thread = threading.Thread(target=download_task)
                thread.daemon = True
                thread.start()
                
                return jsonify({
                    "success": True,
                    "message": f"Download of SuperCollider code pack '{collection_name}' started",
                    "in_progress": True
                })
            elif collection_type == 'reaper':
                from renardo.gatherer.reaper_resource_management.default_reaper_pack import download_reaper_pack, is_reaper_pack_initialized
                
                # Check if already installed
                if is_reaper_pack_initialized(collection_name):
                    logger.write_line(f"Reaper resource pack '{collection_name}' is already installed", "WARN")
                    return jsonify({
                        "success": True,
                        "message": f"Reaper resource pack '{collection_name}' is already installed",
                        "already_installed": True
                    })
                
                # Start download in a separate thread to avoid blocking
                def download_task():
                    try:
                        logger.write_line(f"🚀 STARTING DOWNLOAD: Reaper resource pack '{collection_name}'...", "INFO")
                        logger.write_line(f"Please wait while we prepare and download the reaper resources...", "INFO")
                        success = download_reaper_pack(collection_name, logger)
                        
                        if success:
                            logger.write_line(f"🎉 DOWNLOAD SUCCESSFUL: Reaper resource pack '{collection_name}' has been installed!", "SUCCESS")
                            logger.write_line(f"You can now use these Reaper resources in your compositions.", "SUCCESS")
                            
                            # Broadcast updated status to all WebSocket clients
                            websocket_utils.broadcast_to_clients({
                                "type": "collection_downloaded",
                                "data": {
                                    "type": "reaper",
                                    "name": collection_name,
                                    "success": True
                                }
                            })
                        else:
                            logger.write_error(f"❌ DOWNLOAD FAILED: Reaper resource pack '{collection_name}' could not be installed completely.")
                            logger.write_error(f"Please try again later or contact support if the issue persists.")
                    except Exception as e:
                        logger.write_error(f"❌ ERROR DURING DOWNLOAD: Reaper resource pack '{collection_name}': {str(e)}")
                        logger.write_error(f"Please try again later or check your network connection.")
                
                # Start download thread
                import threading
                thread = threading.Thread(target=download_task)
                thread.daemon = True
                thread.start()
                
                return jsonify({
                    "success": True,
                    "message": f"Download of Reaper resource pack '{collection_name}' started",
                    "in_progress": True
                })
            else:
                return jsonify({
                    "success": False,
                    "message": f"Unknown collection type: {collection_type}"
                }), 400
                
        except Exception as e:
            logger.write_error(f"Error processing download request: {str(e)}")
            return jsonify({
                "success": False,
                "message": f"Error downloading collection: {str(e)}"
            }), 500
            
    @webapp.route('/api/settings', methods=['GET'])
    def get_settings():
        """
        Get all public settings
        
        Returns:
            JSON: All public settings
        """
        try:
            # Return all public settings
            return jsonify({
                "success": True,
                "settings": settings._public_settings
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error fetching settings: {str(e)}"
            }), 500
    
    @webapp.route('/api/settings/<path:setting_path>', methods=['GET'])
    def get_specific_setting(setting_path):
        """
        Get a specific setting by path
        
        Args:
            setting_path (str): Setting path (e.g., "core.CPU_USAGE")
            
        Returns:
            JSON: Setting value
        """
        try:
            # Replace slashes with dots for nested keys
            setting_key = setting_path.replace('/', '.')
            value = settings.get(setting_key, None, internal=False)
            
            if value is None:
                return jsonify({
                    "success": False,
                    "message": f"Setting not found: {setting_key}"
                }), 404
                
            return jsonify({
                "success": True,
                "key": setting_key,
                "value": value
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error fetching setting: {str(e)}"
            }), 500
    
    @webapp.route('/api/settings/<path:setting_path>', methods=['PUT'])
    def update_setting(setting_path):
        """
        Update a specific setting
        
        Args:
            setting_path (str): Setting path (e.g., "core.CPU_USAGE")
            
        Request body:
            {
                "value": <setting value>
            }
            
        Returns:
            JSON: Update status
        """
        try:
            # Get request data
            data = request.get_json()
            
            if not data or 'value' not in data:
                return jsonify({
                    "success": False,
                    "message": "Missing 'value' in request data"
                }), 400
                
            # Replace slashes with dots for nested keys
            setting_key = setting_path.replace('/', '.')
            value = data['value']
            
            # Update the setting
            settings.set(setting_key, value, internal=False)
            
            # Save settings to file
            settings.save_to_file(save_internal=False)
            
            # Broadcast setting change to WebSocket clients
            websocket_utils.broadcast_to_clients({
                "type": "setting_updated",
                "data": {
                    "key": setting_key,
                    "value": value
                }
            })
            
            return jsonify({
                "success": True,
                "key": setting_key,
                "value": value,
                "message": "Setting updated successfully"
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error updating setting: {str(e)}"
            }), 500
            
    @webapp.route('/api/settings/reset', methods=['POST'])
    def reset_settings():
        """
        Reset all settings to defaults
        
        Returns:
            JSON: Reset status
        """
        try:
            # Reset all public settings
            settings.reset(internal=False)
            
            # Save settings to file
            settings.save_to_file(save_internal=False)
            
            # Broadcast reset to WebSocket clients
            websocket_utils.broadcast_to_clients({
                "type": "settings_reset",
                "data": {
                    "settings": settings._public_settings
                }
            })
            
            return jsonify({
                "success": True,
                "message": "Settings reset to defaults",
                "settings": settings._public_settings
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error resetting settings: {str(e)}"
            }), 500
            
    @webapp.route('/api/music-examples/files', methods=['GET'])
    def get_music_example_files():
        """
        Get list of music example files
        
        Returns:
            JSON: List of music example files
        """
        try:
            from renardo.settings_manager import settings
            import os
            from pathlib import Path
            
            examples_dir = settings.get_path("RENARDO_ROOT_PATH") / "music_examples"
            
            if not examples_dir.exists():
                return jsonify({
                    "success": False,
                    "message": "Music examples directory not found",
                    "files": []
                })
            
            files_data = []
            for file_path in sorted(examples_dir.glob("*.py")):
                # Try to extract a description from the first line of the file
                description = ""
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                        if first_line.startswith('#'):
                            description = first_line[1:].strip()
                        else:
                            # Try to find the first comment line
                            f.seek(0)
                            for line in f:
                                if line.strip().startswith('#'):
                                    description = line.strip()[1:].strip()
                                    break
                except:
                    pass
                
                files_data.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "url": f"/api/music-examples/files/{file_path.name}",
                    "description": description
                })
            
            return jsonify({
                "success": True,
                "files": files_data
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error fetching music example files: {str(e)}"
            }), 500
    
    @webapp.route('/api/music-examples/files/<filename>', methods=['GET'])
    def get_music_example_file(filename):
        """
        Get a specific music example file
        
        Args:
            filename (str): Name of the example file
            
        Returns:
            Text: Example file content
        """
        try:
            from renardo.settings_manager import settings
            from pathlib import Path
            
            examples_dir = settings.get_path("RENARDO_ROOT_PATH") / "music_examples"
            file_path = examples_dir / filename
            
            # Security check - ensure the file is within the examples directory
            if not file_path.resolve().is_relative_to(examples_dir.resolve()):
                return jsonify({
                    "success": False,
                    "message": "Access denied"
                }), 403
            
            # Check if file exists
            if not file_path.exists():
                return jsonify({
                    "success": False,
                    "message": "Example file not found"
                }), 404
            
            # Read and return the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Return as plain text
            from flask import Response
            return Response(content, mimetype='text/plain')
            
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error reading example file: {str(e)}"
            }), 500
    
    @webapp.route('/api/tutorial/files', methods=['GET'])
    def get_tutorial_files():
        """
        Get list of tutorial files
        
        Query params:
            lang (optional): Language code (e.g., 'en', 'es'). If not provided, returns all languages.
        
        Returns:
            JSON: List of tutorial file paths organized by language
        """
        try:
            from renardo.settings_manager import settings
            import os
            
            language = request.args.get('lang', None)
            tutorial_base_dir = settings.get_path("RENARDO_ROOT_PATH") / "tutorial"
            
            if language:
                # Return files for specific language
                lang_dir = tutorial_base_dir / language
                if not lang_dir.exists():
                    return jsonify({
                        "success": False,
                        "message": f"Language '{language}' not found"
                    }), 404
                
                files_data = []
                for file_path in sorted(lang_dir.glob("*.py")):
                    files_data.append({
                        "name": file_path.name,
                        "path": str(file_path),
                        "url": f"/api/tutorial/files/{language}/{file_path.name}"
                    })
                
                return jsonify({
                    "success": True,
                    "language": language,
                    "files": files_data
                })
            else:
                # Return all available languages
                languages = {}
                for lang_dir in tutorial_base_dir.iterdir():
                    if lang_dir.is_dir():
                        lang_code = lang_dir.name
                        files_data = []
                        for file_path in sorted(lang_dir.glob("*.py")):
                            files_data.append({
                                "name": file_path.name,
                                "path": str(file_path),
                                "url": f"/api/tutorial/files/{lang_code}/{file_path.name}"
                            })
                        languages[lang_code] = files_data
                
                return jsonify({
                    "success": True,
                    "languages": languages
                })
                
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error fetching tutorial files: {str(e)}"
            }), 500
            
    @webapp.route('/api/documentation/files', methods=['GET'])
    def get_documentation_files():
        """
        Get list of documentation files
        
        Returns:
            JSON: List of documentation file paths
        """
        try:
            from renardo.settings_manager import settings
            import os
            from pathlib import Path
            
            docs_base_dir = settings.get_path("RENARDO_ROOT_PATH") / "docs"
            
            if not docs_base_dir.exists():
                return jsonify({
                    "success": False,
                    "message": "Documentation directory not found",
                    "files": []
                })
            
            # Get all markdown files recursively
            files = []
            
            for root, _, filenames in os.walk(docs_base_dir):
                rel_path = os.path.relpath(root, docs_base_dir)
                
                for filename in filenames:
                    if filename.endswith('.md'):
                        # Create a relative path (for display)
                        if rel_path == '.':
                            display_path = filename
                        else:
                            display_path = os.path.join(rel_path, filename)
                        
                        # Calculate the file path relative to the documentation root
                        file_path = os.path.join(rel_path, filename)
                        
                        # Create the API URL for fetching this file
                        url = f'/api/documentation/file?path={file_path}'
                        
                        # Get the file title (first heading in the file)
                        file_title = get_file_title(os.path.join(root, filename))
                        
                        files.append({
                            'name': filename,
                            'title': file_title or display_path.replace('.md', ''),
                            'path': file_path,
                            'url': url
                        })
            
            # Sort files by path
            files.sort(key=lambda x: x['path'])
            
            return jsonify({
                'success': True,
                'files': files
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error fetching documentation files: {str(e)}'
            }), 500
    
    @webapp.route('/api/documentation/file', methods=['GET'])
    def get_documentation_file():
        """
        Get the content of a specific documentation file
        
        Query params:
            path (str): Path to the documentation file relative to the docs directory
        
        Returns:
            JSON: Documentation file content
        """
        try:
            path = request.args.get('path', '')
            
            if not path:
                return jsonify({
                    'success': False,
                    'message': 'No file path provided'
                })
            
            # Ensure path doesn't contain directory traversal
            if '..' in path:
                return jsonify({
                    'success': False,
                    'message': 'Invalid file path'
                })
            
            from renardo.settings_manager import settings
            docs_path = settings.get_path("RENARDO_ROOT_PATH") / "docs"
            file_path = docs_path / path
            
            if not file_path.exists() or not file_path.is_file():
                return jsonify({
                    'success': False,
                    'message': 'File not found'
                })
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                import markdown
                # Convert markdown to HTML
                html_content = markdown.markdown(
                    content,
                    extensions=['tables', 'fenced_code', 'codehilite']
                )
                
                return jsonify({
                    'success': True,
                    'content': html_content,
                    'raw_content': content
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'Error reading file: {str(e)}'
                })
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error processing documentation file request: {str(e)}'
            }), 500
    
    def get_file_title(file_path):
        """Extract the first heading from a markdown file to use as title."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('# '):
                        return line[2:].strip()
        except:
            pass
        
        return None
    
    @webapp.route('/api/tutorial/files/<lang>/<filename>', methods=['GET'])
    def get_tutorial_file(lang, filename):
        """
        Get a specific tutorial file content
        
        Args:
            lang (str): Language code (e.g., 'en', 'es')
            filename (str): Name of the tutorial file
            
        Returns:
            Text: Tutorial file content
        """
        try:
            from renardo.settings_manager import settings
            import os
            
            tutorial_dir = settings.get_path("RENARDO_ROOT_PATH") / "tutorial" / lang
            file_path = tutorial_dir / filename
            
            # Security check - ensure the file is within the tutorial directory
            if not file_path.resolve().is_relative_to(tutorial_dir.resolve()):
                return "Access denied", 403
                
            # Check if file exists
            if not file_path.exists():
                return "File not found", 404
                
            # Read and return the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            from flask import Response
            return Response(content, mimetype='text/plain')
            
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error reading tutorial file: {str(e)}"
            }), 500
            
    @webapp.route('/api/sessions', methods=['POST'])
    def save_session():
        """
        Save a session file
        
        Request body:
            {
                "filename": "session_name.py",
                "content": "code content"
            }
            
        Returns:
            JSON: Save status
        """
        try:
            data = request.get_json()
            
            if not data or 'filename' not in data or 'content' not in data:
                return jsonify({
                    "success": False,
                    "message": "Missing 'filename' or 'content' in request data"
                }), 400
                
            filename = data['filename']
            content = data['content']
            
            # Ensure filename ends with .py
            if not filename.endswith('.py'):
                filename += '.py'
                
            # Get user directory and create livecoding_sessions subdirectory
            from pathlib import Path
            from renardo.settings_manager import settings
            user_dir = settings.get_renardo_user_dir()
            sessions_dir = user_dir / "livecoding_sessions"
            
            # Create sessions directory if it doesn't exist
            sessions_dir.mkdir(exist_ok=True)
            
            # Save the file
            file_path = sessions_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return jsonify({
                "success": True,
                "message": f"Session saved as {filename}",
                "filename": filename
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error saving session: {str(e)}"
            }), 500
            
    @webapp.route('/api/sessions', methods=['GET'])
    def list_sessions():
        """
        List available session files
        
        Returns:
            JSON: List of session files
        """
        try:
            from pathlib import Path
            from renardo.settings_manager import settings
            user_dir = settings.get_renardo_user_dir()
            sessions_dir = user_dir / "livecoding_sessions"
            
            # Create sessions directory if it doesn't exist
            sessions_dir.mkdir(exist_ok=True)
            
            # List all .py files in sessions directory
            session_files = []
            for file_path in sorted(sessions_dir.glob("*.py")):
                session_files.append({
                    "name": file_path.name,
                    "url": f"/api/sessions/{file_path.name}"
                })
                
            return jsonify({
                "success": True,
                "sessions": session_files
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error listing sessions: {str(e)}"
            }), 500
            
    @webapp.route('/api/sessions/<filename>', methods=['GET'])
    def load_session(filename):
        """
        Load a specific session file
        
        Args:
            filename (str): Name of the session file
            
        Returns:
            JSON: Session content
        """
        try:
            from pathlib import Path
            from renardo.settings_manager import settings
            user_dir = settings.get_renardo_user_dir()
            sessions_dir = user_dir / "livecoding_sessions"
            
            file_path = sessions_dir / filename
            
            # Security check - ensure the file is within the sessions directory
            if not file_path.resolve().is_relative_to(sessions_dir.resolve()):
                return jsonify({
                    "success": False,
                    "message": "Access denied"
                }), 403
                
            # Check if file exists
            if not file_path.exists():
                return jsonify({
                    "success": False,
                    "message": "Session file not found"
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
                "message": f"Error loading session: {str(e)}"
            }), 500
            
    @webapp.route('/api/settings/user-directory', methods=['GET'])
    def get_user_directory():
        """
        Get the current user directory path
        
        Returns:
            JSON: Current user directory path
        """
        try:
            user_dir = settings.get_renardo_user_dir()
            return jsonify({
                "success": True,
                "path": str(user_dir)
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error fetching user directory: {str(e)}"
            }), 500
    
    @webapp.route('/api/settings/user-directory/open', methods=['POST'])
    def open_user_directory():
        """
        Open the user directory in the OS file browser
        
        Returns:
            JSON: Operation status
        """
        try:
            user_dir = settings.get_renardo_user_dir()
            
            # Platform-specific commands to open directory
            if platform.system() == 'Windows':
                subprocess.Popen(['explorer', str(user_dir)])
            elif platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['open', str(user_dir)])
            else:  # Linux and others
                subprocess.Popen(['xdg-open', str(user_dir)])
                
            return jsonify({
                "success": True,
                "message": "User directory opened"
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error opening user directory: {str(e)}"
            }), 500
            
    @webapp.route('/api/settings/user-directory/livecoding-sessions/open', methods=['POST'])
    def open_livecoding_sessions_directory():
        """
        Open the livecoding_sessions directory in the OS file browser
        
        Returns:
            JSON: Operation status
        """
        try:
            user_dir = settings.get_renardo_user_dir()
            sessions_dir = user_dir / "livecoding_sessions"
            
            # Create the directory if it doesn't exist
            sessions_dir.mkdir(exist_ok=True)
            
            # Platform-specific commands to open directory
            if platform.system() == 'Windows':
                subprocess.Popen(['explorer', str(sessions_dir)])
            elif platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['open', str(sessions_dir)])
            else:  # Linux and others
                subprocess.Popen(['xdg-open', str(sessions_dir)])
                
            return jsonify({
                "success": True,
                "message": "Livecoding sessions directory opened"
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error opening livecoding sessions directory: {str(e)}"
            }), 500
    
    @webapp.route('/api/collections/<collection_type>/<collection_name>/structure', methods=['GET'])
    def get_collection_structure(collection_type, collection_name):
        """
        Get the structure of a specific collection (installed or remote)
        
        Args:
            collection_type (str): Type of collection ('reaper')
            collection_name (str): Name of the collection
            
        Returns:
            JSON: Collection structure
        """
        try:
            # Currently only supporting reaper collections
            if collection_type != 'reaper':
                return jsonify({
                    "success": False,
                    "message": f"Collection structure exploration is only supported for reaper collections currently"
                }), 400
            
            # Check if collection is installed
            from renardo.gatherer.reaper_resource_management.default_reaper_pack import is_reaper_pack_initialized
            is_installed = is_reaper_pack_initialized(collection_name)
            
            if is_installed:
                # Fetch structure from local installation
                return get_installed_reaper_collection_structure(collection_name)
            else:
                # Fetch structure from remote server
                return get_remote_reaper_collection_structure(collection_name)
                
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error fetching collection structure: {str(e)}"
            }), 500
    
    def get_installed_reaper_collection_structure(collection_name):
        """
        Get the structure of an installed Reaper collection
        
        Args:
            collection_name (str): Name of the Reaper collection
            
        Returns:
            JSON: Collection structure
        """
        try:
            # Initialize the Reaper resource library
            from renardo.gatherer.reaper_resource_management.reaper_resource_library import ReaperResourceLibrary
            from renardo.lib.music_resource import ResourceType
            
            # Get the collection directory
            collection_path = settings.get_path("REAPER_LIBRARY") / collection_name
            
            # Check if the collection directory exists
            if not collection_path.exists():
                print(f"Collection directory not found: {collection_path}")
                return jsonify({
                    "success": False,
                    "message": f"Collection directory not found: {collection_path}"
                }), 404
            
            print(f"Exploring collection directory: {collection_path}")
            
            # First check if the collection is organized directly without banks
            # i.e. if it has "instrument" or "instruments" directory directly 
            direct_instrument_dir = None
            
            for possible_name in ["instrument", "instruments", "Instrument", "Instruments"]:
                direct_path = collection_path / possible_name
                if direct_path.exists() and direct_path.is_dir():
                    direct_instrument_dir = direct_path
                    print(f"Found direct instruments directory: {direct_path}")
                    break
            
            # Check if we're dealing with a collection without banks
            # (Categories directly in the collection without bank subdirectories)
            if direct_instrument_dir:
                # In this case we'll create a single bank with the collection name
                structure = {
                    "name": collection_name,
                    "banks": [{
                        "name": collection_name,
                        "index": 0,
                        "instruments": [],
                        "effects": []
                    }]
                }
                
                bank_data = structure["banks"][0]
                
                print(f"Checking instrument directories in: {direct_instrument_dir}")
                # Look for category directories
                for category_dir in direct_instrument_dir.iterdir():
                    if category_dir.is_dir():
                        category_name = category_dir.name
                        print(f"Found category: {category_name}")
                        
                        # Get resources in this category
                        resource_files = []
                        for file_path in category_dir.glob("*.py"):
                            if file_path.stem != "__init__":
                                resource_files.append(file_path.stem)
                                
                        print(f"  Category {category_name} has {len(resource_files)} resources: {resource_files}")
                        
                        category_data = {
                            "name": category_name,
                            "resources": []
                        }
                        
                        # Add resources to category
                        for resource_name in resource_files:
                            category_data["resources"].append({
                                "name": resource_name,
                                "type": "instrument"
                            })
                        
                        bank_data["instruments"].append(category_data)
                
                print(f"Created direct collection structure with {len(bank_data['instruments'])} categories")
                
                return jsonify({
                    "success": True,
                    "is_installed": True,
                    "structure": structure
                })
            
            # If we reach here, we're using the standard bank structure
            # Initialize the library
            library = ReaperResourceLibrary(collection_path)
            
            # Build the structure
            structure = {
                "name": collection_name,
                "banks": []
            }
            
            # Debug information
            bank_names = library.list_banks()
            print(f"Found {len(bank_names)} banks in collection {collection_name}: {bank_names}")
            
            # Add each bank
            for bank_idx, bank_name in enumerate(bank_names):
                bank = library.get_bank(bank_idx)
                if not bank:
                    # Try getting the bank by name if index doesn't work
                    bank = library.get_bank_by_name(bank_name)
                
                if not bank:
                    print(f"Could not find bank with index {bank_idx} or name {bank_name}")
                    continue
                
                instrument_categories = bank.list_categories(ResourceType.INSTRUMENT)
                effect_categories = bank.list_categories(ResourceType.EFFECT)
                
                print(f"Bank {bank_name} has {len(instrument_categories)} instrument categories and {len(effect_categories)} effect categories")
                
                bank_data = {
                    "name": bank_name,
                    "index": bank_idx,
                    "instruments": [],
                    "effects": []
                }
                
                # Add instrument categories
                for category_name in instrument_categories:
                    resources = bank.list_resources(ResourceType.INSTRUMENT, category_name)
                    print(f"  Instrument category {category_name} has {len(resources)} resources")
                    
                    category_data = {
                        "name": category_name,
                        "resources": []
                    }
                    
                    # Add resources in this category
                    for resource_name in resources:
                        category_data["resources"].append({
                            "name": resource_name,
                            "type": "instrument"
                        })
                    
                    bank_data["instruments"].append(category_data)
                
                # Add effect categories
                for category_name in effect_categories:
                    resources = bank.list_resources(ResourceType.EFFECT, category_name)
                    print(f"  Effect category {category_name} has {len(resources)} resources")
                    
                    category_data = {
                        "name": category_name,
                        "resources": []
                    }
                    
                    # Add resources in this category
                    for resource_name in resources:
                        category_data["resources"].append({
                            "name": resource_name,
                            "type": "effect"
                        })
                    
                    bank_data["effects"].append(category_data)
                
                structure["banks"].append(bank_data)
            
            print(f"Final structure has {len(structure['banks'])} banks")
            
            return jsonify({
                "success": True,
                "is_installed": True,
                "structure": structure
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error fetching installed collection structure: {str(e)}"
            }), 500
    
    @webapp.route('/api/collections/<collection_type>/<collection_name>/resource/<category>/<resource_name>', methods=['GET'])
    def get_resource_details(collection_type, collection_name, category, resource_name):
        """
        Get details of a specific resource in a collection
        
        Args:
            collection_type (str): Type of collection ('reaper')
            collection_name (str): Name of the collection
            category (str): Category of the resource
            resource_name (str): Name of the resource
            
        Returns:
            JSON: Resource details
        """
        try:
            # Currently only supporting reaper collections
            if collection_type != 'reaper':
                return jsonify({
                    "success": False,
                    "message": f"Resource details are only supported for reaper collections currently"
                }), 400
            
            # Initialize the Reaper resource library
            from renardo.gatherer.reaper_resource_management.reaper_resource_library import ReaperResourceLibrary
            from renardo.lib.music_resource import ResourceType
            
            # Get the collection directory
            collection_path = settings.get_path("REAPER_LIBRARY") / collection_name
            
            # Check if the collection directory exists
            if not collection_path.exists():
                return jsonify({
                    "success": False,
                    "message": f"Collection directory not found: {collection_path}"
                }), 404
                
            # Try to find the resource file
            # First check if we're dealing with the direct structure (instrument/category/resource)
            instrument_dir = None
            for possible_name in ["instrument", "instruments", "Instrument", "Instruments"]:
                direct_path = collection_path / possible_name / category
                if direct_path.exists() and direct_path.is_dir():
                    instrument_dir = direct_path
                    break
            
            if instrument_dir:
                # Look for Python files with the resource name
                py_file = instrument_dir / f"{resource_name}.py"
                rfxchain_file = instrument_dir / f"{resource_name}.RfxChain"
                
                # Prepare response
                response_data = {
                    "success": True,
                    "name": resource_name,
                    "type": "instrument",
                    "category": category,
                    "metadata": {},
                    "content": None
                }
                
                # Add file content if Python file exists
                if py_file.exists():
                    with open(py_file, 'r') as f:
                        response_data["content"] = f.read()
                    
                    # Add metadata
                    response_data["metadata"] = {
                        "file_path": str(py_file),
                        "has_rfxchain": rfxchain_file.exists()
                    }
                    
                    if rfxchain_file.exists():
                        response_data["metadata"]["rfxchain_path"] = str(rfxchain_file)
                    
                    return jsonify(response_data)
                
                # If no Python file but RfxChain exists, return info about the RfxChain
                if rfxchain_file.exists():
                    response_data["metadata"] = {
                        "file_path": str(rfxchain_file),
                        "type": "rfxchain"
                    }
                    
                    # Don't include raw content for RfxChain files, but we could add a summary
                    response_data["content"] = "RfxChain file (binary content)"
                    
                    return jsonify(response_data)
                
                # No files found
                return jsonify({
                    "success": False,
                    "message": f"Resource file not found: {resource_name}"
                }), 404
            
            # If we're here, try the bank structure approach
            # Initialize the library
            library = ReaperResourceLibrary(collection_path)
            
            # Look for the bank that might contain this resource
            banks = library.list_banks()
            for bank_name in banks:
                bank = library.get_bank_by_name(bank_name)
                if not bank:
                    continue
                
                # Try to find the resource in this bank
                resource = bank.get_resource(ResourceType.INSTRUMENT, category, resource_name)
                if resource:
                    # Prepare response
                    response_data = {
                        "success": True,
                        "name": resource_name,
                        "type": "instrument",
                        "category": category,
                        "bank": bank_name,
                        "metadata": {},
                        "content": None
                    }
                    
                    # Add file details
                    response_data["metadata"] = {
                        "file_path": str(resource.full_path),
                        "extension": resource.extension,
                        "size": resource.size
                    }
                    
                    # Add file content if it's a Python file
                    if resource.extension.lower() == '.py':
                        with open(resource.full_path, 'r') as f:
                            response_data["content"] = f.read()
                    elif resource.extension.lower() == '.rfxchain':
                        response_data["content"] = "RfxChain file (binary content)"
                    
                    return jsonify(response_data)
            
            # Resource not found in any bank
            return jsonify({
                "success": False,
                "message": f"Resource not found: {resource_name} in category {category}"
            }), 404
            
        except Exception as e:
            print(f"Error fetching resource details: {e}")
            return jsonify({
                "success": False,
                "message": f"Error fetching resource details: {str(e)}"
            }), 500
    
    def get_remote_reaper_collection_structure(collection_name):
        """
        Get the structure of a remote Reaper collection
        
        Args:
            collection_name (str): Name of the Reaper collection
            
        Returns:
            JSON: Collection structure
        """
        try:
            # Construct the collection index URL
            collection_index_url = '{}/{}/{}/collection_index.json'.format(
                settings.get("core.COLLECTIONS_DOWNLOAD_SERVER"),
                "reaper_library",
                collection_name
            )
            
            # Fetch the collection index
            response = requests.get(collection_index_url, timeout=10)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            # Parse the collection index
            collection_index = response.json()
            
            # Process the collection index into a structured format
            structure = {
                "name": collection_name,
                "banks": []
            }
            
            # Group files by bank/type/category
            banks = {}
            
            for file_info in collection_index.get("files", []):
                file_path = file_info.get("path", "")
                if not file_path.startswith(collection_name):
                    continue
                    
                # Split the path into components
                path_parts = file_path.split("/")
                
                # Skip if not enough parts for bank/type/category/resource structure
                if len(path_parts) < 5:
                    continue
                    
                # Extract components
                bank_name = path_parts[1]  # e.g., "0_renardo_core"
                resource_type = path_parts[2]  # "instruments" or "effects"
                category_name = path_parts[3]  # e.g., "bass", "drums", etc.
                resource_name = path_parts[4]  # e.g., "analog_bass.RfxChain"
                
                # Strip file extension
                if "." in resource_name:
                    resource_name = resource_name.rsplit(".", 1)[0]
                
                # Handle resource types
                if resource_type.lower() not in ["instrument", "instruments", "effect", "effects"]:
                    continue
                    
                normalized_type = "instruments" if resource_type.lower() in ["instrument", "instruments"] else "effects"
                
                # Initialize bank if not exists
                if bank_name not in banks:
                    # Extract bank index from name (assuming format like "0_bank_name")
                    bank_index = 0
                    if "_" in bank_name:
                        try:
                            bank_index = int(bank_name.split("_")[0])
                        except ValueError:
                            pass
                    
                    banks[bank_name] = {
                        "name": bank_name,
                        "index": bank_index,
                        "instruments": {},
                        "effects": {}
                    }
                
                # Initialize category if not exists
                if category_name not in banks[bank_name][normalized_type]:
                    banks[bank_name][normalized_type][category_name] = []
                
                # Add resource to category
                banks[bank_name][normalized_type][category_name].append({
                    "name": resource_name,
                    "type": normalized_type[:-1]  # "instrument" or "effect"
                })
            
            # Convert the nested dictionaries to lists for the final structure
            for bank_name, bank_data in banks.items():
                bank_structure = {
                    "name": bank_name,
                    "index": bank_data["index"],
                    "instruments": [],
                    "effects": []
                }
                
                # Add instrument categories
                for category_name, resources in bank_data["instruments"].items():
                    bank_structure["instruments"].append({
                        "name": category_name,
                        "resources": resources
                    })
                
                # Add effect categories
                for category_name, resources in bank_data["effects"].items():
                    bank_structure["effects"].append({
                        "name": category_name,
                        "resources": resources
                    })
                
                structure["banks"].append(bank_structure)
            
            # Sort banks by index
            structure["banks"].sort(key=lambda x: x["index"])
            
            return jsonify({
                "success": True,
                "is_installed": False,
                "structure": structure
            })
            
        except requests.RequestException as e:
            return jsonify({
                "success": False,
                "message": f"Error fetching remote collection: {str(e)}"
            }), 500
        except json.JSONDecodeError as e:
            return jsonify({
                "success": False,
                "message": f"Error parsing collection JSON: {str(e)}"
            }), 500
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error processing remote collection structure: {str(e)}"
            }), 500
    
    @webapp.route('/api/settings/user-directory/move', methods=['POST'])
    def move_user_directory():
        """
        Move the user directory to a new location
        
        Request body:
            {
                "path": "/new/user/directory/path"
            }
            
        Returns:
            JSON: Operation status
        """
        try:
            data = request.get_json()
            
            if not data or 'path' not in data:
                return jsonify({
                    "success": False,
                    "message": "Missing 'path' in request data"
                }), 400
                
            new_path = data['path']
            from pathlib import Path
            new_dir = Path(new_path)
            
            # Get current user directory
            current_dir = settings.get_renardo_user_dir()
            
            # Validate the new path
            if not new_dir.is_absolute():
                return jsonify({
                    "success": False,
                    "message": "Path must be absolute"
                }), 400
                
            # Check if new directory exists or can be created
            try:
                new_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return jsonify({
                    "success": False,
                    "message": f"Cannot create directory: {str(e)}"
                }), 400
            
            # Move all files from current to new directory
            try:
                # Copy all files and subdirectories
                for item in current_dir.iterdir():
                    if item.is_dir():
                        shutil.copytree(item, new_dir / item.name, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, new_dir / item.name)
                
                # Update user_dir.toml with new path
                settings.set_user_dir_path(new_dir)
                
                # Save current settings to ensure they're persisted
                settings.save_to_file()
                
                return jsonify({
                    "success": True,
                    "message": "User directory moved successfully",
                    "path": str(new_dir)
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "message": f"Error moving files: {str(e)}"
                }), 500
                
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error moving user directory: {str(e)}"
            }), 500

    @webapp.route('/api/settings/toml', methods=['GET'])
    def get_toml_settings():
        """
        Get the raw TOML settings file content
        
        Returns:
            JSON: {"toml": "raw TOML content"}
        """
        try:
            # Get the settings file path
            settings_file = settings.public_file
            
            # Read the raw TOML content
            if settings_file.exists():
                toml_content = settings_file.read_text(encoding='utf-8')
            else:
                # Return empty TOML if file doesn't exist
                toml_content = "# Renardo Settings\n"
                
            return jsonify({
                "success": True,
                "toml": toml_content
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error reading TOML settings: {str(e)}"
            }), 500

    @webapp.route('/api/settings/toml', methods=['PUT'])
    def save_toml_settings():
        """
        Save raw TOML settings directly to the settings file
        
        Expected JSON body:
            {"toml": "raw TOML content"}
        
        Returns:
            JSON: Success/error response
        """
        try:
            data = request.get_json()
            if not data or 'toml' not in data:
                return jsonify({
                    "success": False,
                    "message": "Missing 'toml' field in request body"
                }), 400
            
            toml_content = data['toml']
            
            # Validate TOML syntax
            try:
                # Parse the TOML to validate syntax
                parsed_toml = tomli.loads(toml_content)
            except tomli.TOMLDecodeError as e:
                return jsonify({
                    "success": False,
                    "message": f"TOML syntax error: {str(e)}"
                }), 400
            
            # Get the settings file path
            settings_file = settings.public_file
            
            # Write the TOML content directly to the file
            settings_file.write_text(toml_content, encoding='utf-8')
            
            # Reload settings from the file to update internal state
            settings.load_from_file()
            
            # Broadcast settings update via WebSocket
            websocket_utils.broadcast_to_clients({
                "type": "settings_updated",
                "data": {
                    "settings": settings._public_settings
                }
            })
            
            return jsonify({
                "success": True,
                "message": "TOML settings saved successfully",
                "settings": settings._public_settings
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error saving TOML settings: {str(e)}"
            }), 500