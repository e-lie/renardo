from datetime import datetime
from pathlib import Path
import os

from renardo.settings_manager import settings
from renardo.gatherer.collection_download import download_files_from_json_index_concurrent

def is_default_reaper_pack_initialized():
    """Check if the default Reaper resource pack has been downloaded."""
    default_pack_name = settings.get("reaper_backend.DEFAULT_REAPER_PACK_NAME", "0_renardo_core")
    return (settings.get_path("REAPER_LIBRARY") / default_pack_name / 'downloaded_at.txt').exists()

def is_reaper_pack_initialized(pack_name):
    """Check if a specific Reaper resource pack has been downloaded."""
    return (settings.get_path("REAPER_LIBRARY") / pack_name / 'downloaded_at.txt').exists()

def ensure_default_reaper_pack():
    """Ensure the default Reaper resource pack is initialized.
    
    This function checks if the default Reaper resource pack is already initialized,
    and if not, attempts to download and initialize it.
    
    Returns:
        bool: True if the default pack is available (either already initialized or successfully downloaded)
    """
    default_pack_name = settings.get("reaper_backend.DEFAULT_REAPER_PACK_NAME", "0_renardo_core")
    
    # Check if already initialized
    if is_default_reaper_pack_initialized():
        print(f"Default Reaper resource pack '{default_pack_name}' is already initialized")
        return True
    
    # Initialize the pack
    print(f"Initializing default Reaper resource pack: {default_pack_name}")
    download_success = download_reaper_pack(default_pack_name)
    
    if download_success:
        print(f"Successfully initialized default Reaper resource pack: {default_pack_name}")
        return True
    else:
        print(f"Failed to initialize default Reaper resource pack: {default_pack_name}")
        return False

def download_reaper_pack(pack_name, logger=None):
    """Download a specific Reaper resource pack.
    
    Args:
        pack_name (str): The name of the Reaper resource pack to download
        logger: Logger instance for output messages
        
    Returns:
        bool: True if the download was successful, False otherwise
    """
    if logger:
        logger.write_line(
            f"Downloading Reaper Resources Pack {pack_name} from {settings.get('core.COLLECTIONS_DOWNLOAD_SERVER')}\n"
        )
    
    # Construct Reaper resource pack URL
    json_url = '{}/{}/{}/collection_index.json'.format(
        settings.get("core.COLLECTIONS_DOWNLOAD_SERVER"),
        "reaper_library",  # This should be the directory on the server
        pack_name
    )
    
    try:
        # Create the directory if it doesn't exist
        download_dir = settings.get_path("REAPER_LIBRARY")
        download_dir.mkdir(exist_ok=True, parents=True)
        
        # Download the Reaper resource pack
        success = download_files_from_json_index_concurrent(
            json_url=json_url,
            download_dir=download_dir,
            logger=logger
        )
        
        if not success:
            if logger:
                logger.write_error(f"Failed to download Reaper resource pack {pack_name}")
            return False
        
        # Create a downloaded_at file to mark this pack as initialized
        download_path = settings.get_path("REAPER_LIBRARY") / pack_name
        download_path.mkdir(exist_ok=True)
        
        with open(download_path / 'downloaded_at.txt', mode="w") as file:
            file.write(str(datetime.now()))
            
        if logger:
            logger.write_line(f"Reaper resource pack {pack_name} downloaded successfully!")
            
        return True
    except Exception as e:
        error_msg = f"Error downloading Reaper resource pack {pack_name}: {str(e)}"
        print(error_msg)
        if logger:
            logger.write_error(error_msg)
        return False