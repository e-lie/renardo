import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin

import requests


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
    download_dir = str(download_dir)

    def download_json_index_from_url(url, logger=logger):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if logger:
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
    if logger:
        logger.write_line(f"Downloading collection index from {json_url}")
    
    file_tree = download_json_index_from_url(json_url)
    if not file_tree:
        if logger:
            logger.write_line("Failed to download collection index")
        return False

    # Generate list of all files to download
    download_tasks = process_node(file_tree, json_url)
    total_files = len(download_tasks)
    
    if logger:
        logger.write_line(f"Found {total_files} files to download")
    
    # Use ThreadPoolExecutor to download files concurrently
    completed_files = 0
    success_count = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(download_file_in_pool, url, path, 5, 1, logger)
            for url, path in download_tasks
        ]
        for future in as_completed(futures):
            # Handle each completed download here
            completed_files += 1
            result = future.result()
            
            if result:
                success_count += 1
            else:
                if logger:
                    logger.write_line("A download failed.")
            
            # Log progress periodically
            if logger and completed_files % 5 == 0:
                logger.write_line(f"Progress: {completed_files}/{total_files} files downloaded")
    
    if logger:
        logger.write_line(f"Download complete: {success_count}/{total_files} files downloaded successfully")
    
    # Return True if all downloads were successful
    return success_count == total_files

