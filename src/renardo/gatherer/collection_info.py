"""
Functions for retrieving collection information from the Renardo collections server
"""
import requests
import json
from typing import Dict, List, Optional

from renardo.settings_manager import settings

def fetch_available_collections(collection_type: str) -> List[Dict]:
    """
    Fetch available collections of a specific type from the collections server.
    
    Args:
        collection_type (str): Type of collection ('samples', 'sccode', or 'reaper')
        
    Returns:
        List[Dict]: List of collection information dictionaries
    """
    # Determine the directory name based on collection type
    if collection_type == 'samples':
        dir_name = settings.get("samples.SAMPLES_DIR_NAME")
    elif collection_type == 'sccode':
        dir_name = settings.get("sc_backend.SCCODE_LIBRARY_DIR_NAME")
    elif collection_type == 'reaper':
        dir_name = "reaper_library"
    else:
        raise ValueError(f"Unknown collection type: {collection_type}")
    
    # Construct the URL for the collections index
    collections_url = '{}/{}/index.json'.format(
        settings.get("core.COLLECTIONS_DOWNLOAD_SERVER"),
        dir_name
    )
    
    try:
        # Fetch the collections index
        response = requests.get(collections_url, timeout=10)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Parse the JSON response
        collections = response.json()
        
        # Return the collections list
        return collections.get('collections', [])
    except requests.RequestException as e:
        print(f"Error fetching collections: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing collections JSON: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error fetching collections: {e}")
        return []

def get_collection_status(collection_type: str, collection_name: str) -> Dict:
    """
    Check if a specific collection is installed and get its metadata.
    
    Args:
        collection_type (str): Type of collection ('samples', 'sccode', or 'reaper')
        collection_name (str): Name of the collection
        
    Returns:
        Dict: Dictionary with collection status information
    """
    # Import the appropriate check function based on collection type
    if collection_type == 'samples':
        from renardo.gatherer.sample_management.default_samples import is_sample_pack_initialized
        
        # Check if the collection is installed
        is_installed = is_sample_pack_initialized(collection_name)
        
        # Check if it's the default collection
        is_default = collection_name == settings.get("samples.DEFAULT_SAMPLE_PACK_NAME")
    
    elif collection_type == 'sccode':
        from renardo.gatherer.sccode_management.default_sccode_pack import is_sccode_pack_initialized
        
        # Check if the collection is installed
        is_installed = is_sccode_pack_initialized(collection_name)
        
        # Check if it's the default collection
        is_default = collection_name == settings.get("sc_backend.DEFAULT_SCCODE_PACK_NAME")

    elif collection_type == 'reaper':
        from renardo.gatherer.reaper_resource_management.default_reaper_pack import is_reaper_pack_initialized
        
        # Check if the collection is installed
        is_installed = is_reaper_pack_initialized(collection_name)
        
        # Check if it's the default collection
        is_default = collection_name == settings.get("reaper_backend.DEFAULT_REAPER_PACK_NAME", "0_renardo_core")
    
    else:
        raise ValueError(f"Unknown collection type: {collection_type}")
    
    # Return the status information
    return {
        "name": collection_name,
        "type": collection_type,
        "installed": is_installed,
        "is_default": is_default
    }

def get_all_collections_info() -> Dict:
    """
    Get information about all available collections and their installation status.
    
    Returns:
        Dict: Dictionary with collections information
    """
    # Get all available sample collections
    sample_collections = fetch_available_collections('samples')
    
    # Get status for each sample collection
    samples_info = []
    for collection in sample_collections:
        collection_name = collection.get('name')
        if collection_name:
            status = get_collection_status('samples', collection_name)
            # Add metadata from the collection info
            status.update({
                "description": collection.get('description', ''),
                "version": collection.get('version', ''),
                "author": collection.get('author', ''),
                "size": collection.get('size', 'Unknown'),
                "tags": collection.get('tags', [])
            })
            samples_info.append(status)
    
    # Get all available sccode collections
    sccode_collections = fetch_available_collections('sccode')
    
    # Get status for each sccode collection
    sccode_info = []
    for collection in sccode_collections:
        collection_name = collection.get('name')
        if collection_name:
            status = get_collection_status('sccode', collection_name)
            # Add metadata from the collection info
            status.update({
                "description": collection.get('description', ''),
                "version": collection.get('version', ''),
                "author": collection.get('author', ''),
                "size": collection.get('size', 'Unknown'),
                "tags": collection.get('tags', [])
            })
            sccode_info.append(status)
    
    # Get all available reaper resource collections
    reaper_collections = fetch_available_collections('reaper')
    
    # Get status for each reaper resource collection
    reaper_info = []
    for collection in reaper_collections:
        collection_name = collection.get('name')
        if collection_name:
            status = get_collection_status('reaper', collection_name)
            # Add metadata from the collection info
            status.update({
                "description": collection.get('description', ''),
                "version": collection.get('version', ''),
                "author": collection.get('author', ''),
                "size": collection.get('size', 'Unknown'),
                "tags": collection.get('tags', [])
            })
            reaper_info.append(status)
    
    # Return all collections information
    return {
        "samples": samples_info,
        "sccode": sccode_info,
        "reaper": reaper_info,
        "collections_server": settings.get("core.COLLECTIONS_DOWNLOAD_SERVER")
    }