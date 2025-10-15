from datetime import datetime
from pathlib import Path
import os

from renardo.settings_manager import settings
from renardo.gatherer.collection_download import download_files_from_json_index_concurrent

def is_default_spack_initialized():
    """Check if the default sample pack has been downloaded."""
    return (settings.get_path("SAMPLES_DIR") / settings.get("samples.DEFAULT_SAMPLE_PACK_NAME") / 'downloaded_at.txt').exists()


def is_sample_pack_initialized(pack_name):
    """Check if a specific sample pack has been downloaded."""
    return (settings.get_path("SAMPLES_DIR") / pack_name / 'downloaded_at.txt').exists()


def download_default_sample_pack(logger=None):
    """Download the default sample pack."""
    # Use default sample pack name from settings
    pack_name = settings.get("samples.DEFAULT_SAMPLE_PACK_NAME")
    
    return download_sample_pack(pack_name, logger)


def download_sample_pack(pack_name, logger=None):
    """Download a specific sample pack.
    
    Args:
        pack_name (str): The name of the sample pack to download
        logger: Logger instance for output messages
        
    Returns:
        bool: True if the download was successful, False otherwise
    """
    if logger:
        logger.write_line(
            f"Downloading Sample Pack {pack_name} from {settings.get('core.COLLECTIONS_DOWNLOAD_SERVER')}\n"
        )
    
    # Construct sample pack URL
    json_url = '{}/{}/{}/collection_index.json'.format(
        settings.get("core.COLLECTIONS_DOWNLOAD_SERVER"),
        settings.get("samples.SAMPLES_DIR_NAME"),
        pack_name
    )
    
    try:
        # Create the directory if it doesn't exist
        download_dir = settings.get_path("SAMPLES_DIR")
        download_dir.mkdir(parents=True, exist_ok=True)
        
        # Download the sample pack
        download_files_from_json_index_concurrent(
            json_url=json_url,
            download_dir=download_dir,
            logger=logger
        )
        
        # Create a downloaded_at file to mark this pack as initialized
        download_path = settings.get_path("SAMPLES_DIR") / pack_name
        download_path.mkdir(exist_ok=True)
        
        with open(download_path / 'downloaded_at.txt', mode="w") as file:
            file.write(str(datetime.now()))
            
        if logger:
            logger.write_line(f"Sample pack {pack_name} downloaded successfully!")
            
        return True
    except Exception as e:
        error_msg = f"Error downloading sample pack {pack_name}: {str(e)}"
        print(error_msg)
        if logger:
            logger.write_error(error_msg)
        return False

