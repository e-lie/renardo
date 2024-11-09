import os
import requests
import time
from datetime import datetime
from renardo_gatherer.config_dir import SAMPLES_DIR_PATH
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

SAMPLES_DOWNLOAD_SERVER = 'https://collections.renardo.org/samples'
# DEFAULT_SAMPLES_PACK_NAME = '0_foxdot_default_testing'
DEFAULT_SAMPLES_PACK_NAME = '0_foxdot_default'
LOOP_SUBDIR = '_loop_'

def ensure_renardo_samples_directory():
    if not SAMPLES_DIR_PATH.exists():
        SAMPLES_DIR_PATH.mkdir(parents=True, exist_ok=True)

def download_file_in_pool(url, dest_path, retries=5, delay=1, logger=None):
    filename = os.path.basename(urlparse(url).path)
    for attempt in range(retries):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            if logger:
                logger.write_line(f"Downloaded {filename} to {dest_path}")
            return True
        except requests.RequestException as e:
            if logger:
                logger.write_line(f"Error downloading {url}: {e}")
            if attempt < retries - 1:
                if logger:
                    logger.write_line(f"Retrying ({attempt + 1}/{retries})...")
                time.sleep(delay)
            else:
                if logger:
                    logger.write_line(f"Failed to download {url} after {retries} attempts")
                return False

                
def download_files_from_json_index_concurrent(json_url, download_dir, max_workers=3, logger=None):
    def download_json_index_from_url(url, logger=logger):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.write_line(f"Error downloading collection JSON index: {e}")
            return None

    def process_node(node, base_url="", current_dir=""):
        tasks = []
        if "url" in node:
            # Full file download URL
            file_url = urljoin(base_url, node["url"])
            # Full local path including any subdirectory structure
            file_path = os.path.join(download_dir, current_dir, os.path.basename(node["path"]))
            tasks.append((file_url, file_path))
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if "children" in node:
            for child in node["children"]:
                # For each child, pass its directory structure down the chain
                child_dir = os.path.join(current_dir, os.path.basename(node["path"]))
                tasks.extend(process_node(child, base_url, child_dir))
                os.makedirs(child_dir, exist_ok=True)
        return tasks

    # Ensure the download directory exists
    os.makedirs(download_dir, exist_ok=True)

    # Download JSON content from URL
    file_tree = download_json_index_from_url(json_url)

    # Generate list of all files to download
    download_tasks = process_node(file_tree, json_url)

    # Use ThreadPoolExecutor to download files concurrently
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(download_file_in_pool, url, path, 5, 1, logger)
            for url, path in download_tasks
        ]
        for future in as_completed(futures):
            # Handle each completed download here if needed (e.g., check for success)
            result = future.result()
            if not result:
                if logger:
                    logger.write_line("A download failed.")


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


def is_default_spack_initialized():
    return (SAMPLES_DIR_PATH / DEFAULT_SAMPLES_PACK_NAME / 'downloaded_at.txt').exists()