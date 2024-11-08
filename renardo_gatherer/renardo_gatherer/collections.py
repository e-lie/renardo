import os
import requests
import time
from datetime import datetime
from renardo_gatherer.config_dir import SAMPLES_DIR_PATH

SAMPLES_DOWNLOAD_SERVER = 'https://collections.renardo.org/samples'
# DEFAULT_SAMPLES_PACK_NAME = '0_foxdot_default_testing'
DEFAULT_SAMPLES_PACK_NAME = '0_foxdot_default'
LOOP_SUBDIR = '_loop_'

def ensure_renardo_samples_directory():
    if not SAMPLES_DIR_PATH.exists():
        SAMPLES_DIR_PATH.mkdir(parents=True, exist_ok=True)

def download_collection_json_index_from_url(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status
    return response.json()


def download_files_from_json_index(json_url, download_dir, logger=None):

    def download_file(url, destination, retries=5, logger=logger):
        attempt = 1
        while attempt <= retries:
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                with open(destination, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                if logger:
                    try:
                        logger.write_line(f"Downloaded {destination}")
                    except Exception as e:
                        print(e)
                else:
                    print(f"Downloaded {destination}")
                return  # Successful download, exit the function
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt} failed for {url}: {e}")
                attempt += 1
                if attempt <= retries:
                    time.sleep(1)  # Wait before retrying
        print(f"Failed to download {url} after {retries} attempts")

    def process_node(node, base_path):
        if "url" in node:
            # This is a file node; download it
            file_path = os.path.join(base_path, node["name"])
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            download_file(node["url"], file_path)
        elif "children" in node:
            # This is a folder node; process its children
            folder_path = os.path.join(base_path, node["name"])
            os.makedirs(folder_path, exist_ok=True)
            for child in node["children"]:
                process_node(child, folder_path)

    file_tree = download_collection_json_index_from_url(json_url)

    process_node(file_tree, download_dir)
    print(f"All files downloaded to {download_dir}")


def download_default_sample_pack(logger=None):

    download_files_from_json_index(
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