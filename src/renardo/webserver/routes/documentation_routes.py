from flask import Blueprint, jsonify, send_from_directory, request
import os
import markdown
from pathlib import Path

# Create a Blueprint for documentation routes
documentation_routes = Blueprint('documentation_routes', __name__)

# Get the base path for documentation files
def get_docs_path():
    # Path to the documentation files
    return Path(__file__).parent.parent.parent / 'docs'

@documentation_routes.route('/api/documentation/files', methods=['GET'])
def get_documentation_files():
    """Get a list of available documentation files."""
    docs_path = get_docs_path()
    
    if not docs_path.exists():
        return jsonify({
            'success': False,
            'message': 'Documentation directory not found',
            'files': []
        })
    
    # Get all markdown files recursively
    files = []
    
    for root, _, filenames in os.walk(docs_path):
        rel_path = os.path.relpath(root, docs_path)
        
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

@documentation_routes.route('/api/documentation/file', methods=['GET'])
def get_documentation_file():
    """Get the content of a specific documentation file."""
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
    
    docs_path = get_docs_path()
    file_path = docs_path / path
    
    if not file_path.exists() or not file_path.is_file():
        return jsonify({
            'success': False,
            'message': 'File not found'
        })
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
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