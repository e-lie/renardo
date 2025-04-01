from datetime import datetime
from pathlib import Path

from renardo.settings_manager import DEFAULT_SAMPLES_PACK_NAME, SAMPLES_DIR_PATH, SAMPLES_DOWNLOAD_SERVER
from renardo.gatherer.collection_download import download_files_from_json_index_concurrent

def is_default_spack_initialized():
    return (SAMPLES_DIR_PATH / DEFAULT_SAMPLES_PACK_NAME / 'downloaded_at.txt').exists()


def default_loop_path() -> Path:
    return SAMPLES_DIR_PATH/DEFAULT_SAMPLES_PACK_NAME/LOOP_SUBDIR


def download_default_sample_pack(logger=None):

    logger.write_line(f"Downloading Default Sample Pack {DEFAULT_SAMPLES_PACK_NAME} from {SAMPLES_DOWNLOAD_SERVER}\n")
    download_files_from_json_index_concurrent(
        json_url=f'{SAMPLES_DOWNLOAD_SERVER}/{DEFAULT_SAMPLES_PACK_NAME}/collection_index.json',
        download_dir=SAMPLES_DIR_PATH,
        logger=logger
    )

    try:
        with open(SAMPLES_DIR_PATH / DEFAULT_SAMPLES_PACK_NAME / 'downloaded_at.txt', mode="w") as file:
            file.write(str(datetime.now()))
    except Exception as e:
        print(e)

