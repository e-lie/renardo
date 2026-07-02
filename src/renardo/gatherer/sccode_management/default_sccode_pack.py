from datetime import datetime
from pathlib import Path
import os
import shutil

from renardo.settings_manager import settings
from renardo.gatherer.collection_download import (
    download_files_from_json_index_concurrent,
    get_file_paths_from_json_index,
)

def _write_marker(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    with open(path / 'downloaded_at.txt', mode='w') as f:
        f.write(str(datetime.now()))


def _bundled_special_sccode_dir() -> Path:
    """Special sccode files shipped with the renardo package (no network download needed)."""
    return settings.get_path("RENARDO_ROOT_PATH") / "sc_backend" / "special_sccode"


def is_default_sccode_pack_initialized():
    """Check if the default SuperCollider code pack has been downloaded."""
    return (settings.get_path("SCCODE_LIBRARY") / settings.get("sc_backend.DEFAULT_SCCODE_PACK_NAME") / 'downloaded_at.txt').exists()


def is_special_sccode_initialized():
    """Check if the special SuperCollider code files have been downloaded."""
    return (settings.get_path("SPECIAL_SCCODE_DIR") / 'downloaded_at.txt').exists()


def is_sccode_pack_initialized(pack_name):
    """Check if a specific SuperCollider code pack has been downloaded."""
    return (settings.get_path("SCCODE_LIBRARY") / pack_name / 'downloaded_at.txt').exists()


def verify_special_sccode_pack() -> bool:
    """Verify all bundled special sccode files are present in the user dir.

    Returns True if complete, False if any file is missing.
    """
    source_dir = _bundled_special_sccode_dir()
    special_sccode_dir = settings.get_path("SPECIAL_SCCODE_DIR")
    if special_sccode_dir is None or not source_dir.exists():
        return False
    return all(
        (special_sccode_dir / source_path.relative_to(source_dir)).exists()
        for source_path in source_dir.rglob('*')
        if source_path.is_file()
    )


def verify_sccode_pack(pack_name) -> bool:
    """Verify all files from the sccode pack collection index exist on disk.

    Returns True if complete, False if any file is missing or the index is unreachable.
    """
    sccode_library = settings.get_path("SCCODE_LIBRARY")
    if sccode_library is None:
        return False
    json_url = '{}/{}/{}/collection_index.json'.format(
        settings.get("core.COLLECTIONS_DOWNLOAD_SERVER"),
        settings.get("sc_backend.SCCODE_LIBRARY_DIR_NAME"),
        pack_name,
    )
    expected = get_file_paths_from_json_index(json_url, sccode_library)
    if expected is None:
        return False
    return all(p.exists() for p in expected)


def backfill_sccode_markers() -> None:
    """Create missing downloaded_at.txt markers for complete sccode packs on disk."""
    special_dir = settings.get_path("SPECIAL_SCCODE_DIR")
    if special_dir is not None and not (special_dir / 'downloaded_at.txt').exists() and verify_special_sccode_pack():
        _write_marker(special_dir)

    sccode_library = settings.get_path("SCCODE_LIBRARY")
    if sccode_library is not None:
        pack_name = settings.get("sc_backend.DEFAULT_SCCODE_PACK_NAME")
        pack_dir = sccode_library / pack_name
        if not (pack_dir / 'downloaded_at.txt').exists() and verify_sccode_pack(pack_name):
            _write_marker(pack_dir)


def provision_special_sccode_pack(logger=None):
    """Copy the special SuperCollider code files bundled with renardo into the user dir."""
    source_dir = _bundled_special_sccode_dir()
    destination_dir = settings.get_path("SPECIAL_SCCODE_DIR")

    if logger:
        logger.info(f"Provisioning special sccode from {source_dir}\n")

    try:
        shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
        _write_marker(destination_dir)

        if logger:
            logger.info("Special SCLang code provisioned successfully!")
        return True
    except Exception as e:
        error_msg = f"Error provisioning special sccode: {str(e)}"
        print(error_msg)
        if logger:
            logger.error(error_msg)
        return False


def download_sccode_pack(pack_name, logger=None):
    """Download a specific SuperCollider code pack.
    
    Args:
        pack_name (str): The name of the SuperCollider code pack to download
        logger: Logger instance for output messages
        
    Returns:
        bool: True if the download was successful, False otherwise
    """
    if logger:
        logger.info(
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
            logger.info(f"SuperCollider code pack {pack_name} downloaded successfully!")
            
        return True
    except Exception as e:
        error_msg = f"Error downloading SuperCollider code pack {pack_name}: {str(e)}"
        print(error_msg)
        if logger:
            logger.error(error_msg)
        return False

