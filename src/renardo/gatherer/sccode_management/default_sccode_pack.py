from datetime import datetime
from pathlib import Path
import os

from renardo.settings_manager import settings
from renardo.gatherer.collection_download import download_files_from_json_index_concurrent

def is_default_sccode_pack_initialized():
    """Check if the default SuperCollider code pack has been downloaded."""
    return (settings.get_path("SCCODE_LIBRARY") / settings.get("sc_backend.DEFAULT_SCCODE_PACK_NAME") / 'downloaded_at.txt').exists()


def is_special_sccode_initialized():
    """Check if the special SuperCollider code files have been downloaded."""
    return (settings.get_path("SPECIAL_SCCODE_DIR") / 'downloaded_at.txt').exists()


def is_sccode_pack_initialized(pack_name):
    """Check if a specific SuperCollider code pack has been downloaded."""
    return (settings.get_path("SCCODE_LIBRARY") / pack_name / 'downloaded_at.txt').exists()


def download_special_sccode_pack(logger=None):
    """Download the default SuperCollider code pack and special code files."""
    success = True
    
    # Download special code files first
    if logger:
        logger.write_line(
            "Downloading core sccode from {}\n".format(
                settings.get("core.COLLECTIONS_DOWNLOAD_SERVER")
            )
        )
    
    try:
        success = download_files_from_json_index_concurrent(
            json_url='{}/{}/collection_index.json'.format(
                settings.get("core.COLLECTIONS_DOWNLOAD_SERVER"),
                settings.get("sc_backend.SPECIAL_SCCODE_DIR_NAME"),
            ),
            download_dir=settings.get_path("SPECIAL_SCCODE_DIR").parent,
            logger=logger
        )
        
        if success:
            # Create a downloaded_at file to mark this as initialized
            download_path = settings.get_path("SPECIAL_SCCODE_DIR")
            download_path.mkdir(exist_ok=True)
            
            from datetime import datetime
            with open(download_path / 'downloaded_at.txt', mode="w") as file:
                file.write(str(datetime.now()))
                
            if logger:
                logger.write_line("Special SCLang code downloaded successfully!")
    except Exception as e:
        error_msg = f"Error downloading special sccode: {str(e)}"
        print(error_msg)
        if logger:
            logger.write_error(error_msg)
        success = False
    
    # Return overall success
    return success


def download_sccode_pack(pack_name, logger=None):
    """Download a specific SuperCollider code pack.
    
    Args:
        pack_name (str): The name of the SuperCollider code pack to download
        logger: Logger instance for output messages
        
    Returns:
        bool: True if the download was successful, False otherwise
    """
    if logger:
        logger.write_line(
            f"Downloading Instruments and Effects Pack {pack_name} from {settings.get('core.COLLECTIONS_DOWNLOAD_SERVER')}\n"
        )
    
    # Construct SC code pack URL
    json_url = '{}/{}/{}/collection_index.json'.format(
        settings.get("core.COLLECTIONS_DOWNLOAD_SERVER"),
        settings.get("sc_backend.SCCODE_LIBRARY_DIR_NAME"),
        pack_name
    )
    
    try:
        # Create the directory if it doesn't exist
        download_dir = settings.get_path("SCCODE_LIBRARY")
        download_dir.mkdir(exist_ok=True)
        
        # Download the SC code pack
        download_files_from_json_index_concurrent(
            json_url=json_url,
            download_dir=download_dir,
            logger=logger
        )
        
        # Create a downloaded_at file to mark this pack as initialized
        download_path = settings.get_path("SCCODE_LIBRARY") / pack_name
        download_path.mkdir(exist_ok=True)
        
        with open(download_path / 'downloaded_at.txt', mode="w") as file:
            file.write(str(datetime.now()))
            
        if logger:
            logger.write_line(f"SuperCollider code pack {pack_name} downloaded successfully!")
            
        return True
    except Exception as e:
        error_msg = f"Error downloading SuperCollider code pack {pack_name}: {str(e)}"
        print(error_msg)
        if logger:
            logger.write_error(error_msg)
        return False

