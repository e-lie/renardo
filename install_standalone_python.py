#!/usr/bin/env python3
"""
Download and install Python standalone distribution for Electron packaging.
This script downloads the appropriate Python distribution based on the current OS and architecture
from https://github.com/indygreg/python-build-standalone/releases
"""

import os
import sys
import platform
import urllib.request
import tarfile
import zipfile
import shutil
from pathlib import Path
import json

PYTHON_VERSION = "3.12.7"
BASE_URL = f"https://github.com/indygreg/python-build-standalone/releases/download/20241016/cpython-{PYTHON_VERSION}+20241016"

def get_platform_info():
    """Detect current platform and return the appropriate download URL and archive name."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Map platform info to python-build-standalone naming
    if system == "linux":
        if machine in ["x86_64", "amd64"]:
            arch = "x86_64"
            variant = "unknown-linux-gnu"
            ext = "tar.gz"
        elif machine in ["aarch64", "arm64"]:
            arch = "aarch64"
            variant = "unknown-linux-gnu"
            ext = "tar.gz"
        else:
            raise RuntimeError(f"Unsupported Linux architecture: {machine}")
            
        archive_name = f"cpython-{PYTHON_VERSION}+20241016-{arch}-{variant}-install_only.{ext}"
        
    elif system == "darwin":  # macOS
        if machine in ["x86_64", "amd64"]:
            arch = "x86_64"
        elif machine in ["arm64", "aarch64"]:
            arch = "aarch64"
        else:
            raise RuntimeError(f"Unsupported macOS architecture: {machine}")
            
        archive_name = f"cpython-{PYTHON_VERSION}+20241016-{arch}-apple-darwin-install_only.tar.gz"
        ext = "tar.gz"
        
    elif system == "windows":
        if machine in ["amd64", "x86_64"]:
            arch = "x86_64"
        elif machine in ["i386", "i686"]:
            arch = "i686"
        else:
            raise RuntimeError(f"Unsupported Windows architecture: {machine}")
            
        archive_name = f"cpython-{PYTHON_VERSION}+20241016-{arch}-pc-windows-msvc-shared-install_only.tar.gz"
        ext = "tar.gz"
        
    else:
        raise RuntimeError(f"Unsupported operating system: {system}")
    
    return {
        "url": f"{BASE_URL}-{arch}-{variant if system == 'linux' else ('apple-darwin' if system == 'darwin' else 'pc-windows-msvc-shared')}-install_only.{ext}",
        "archive_name": archive_name,
        "extension": ext,
        "system": system,
        "arch": arch
    }

def download_file(url, dest_path):
    """Download a file with progress indicator."""
    print(f"Downloading: {url}")
    
    def report_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(downloaded * 100 / total_size, 100) if total_size > 0 else 0
        bar_length = 40
        filled_length = int(bar_length * percent / 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        sys.stdout.write(f'\r|{bar}| {percent:.1f}% ({downloaded / 1024 / 1024:.1f}/{total_size / 1024 / 1024:.1f} MB)')
        sys.stdout.flush()
    
    urllib.request.urlretrieve(url, dest_path, report_progress)
    print()  # New line after progress bar

def extract_archive(archive_path, dest_dir, extension):
    """Extract tar.gz or zip archive."""
    print(f"Extracting archive to {dest_dir}...")
    
    if extension in ["tar.gz", "tgz"]:
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(dest_dir)
    elif extension == "zip":
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(dest_dir)
    else:
        raise ValueError(f"Unknown archive extension: {extension}")
    
    print("Extraction complete!")

def main():
    # Determine paths
    script_dir = Path(__file__).parent
    webclient_dir = script_dir / "webclient"
    python_dir = webclient_dir / "python"
    
    # Check if already installed
    if python_dir.exists():
        response = input(f"Python standalone already exists at {python_dir}. Replace it? (y/n): ")
        if response.lower() != 'y':
            print("Installation cancelled.")
            return
        print(f"Removing existing installation...")
        shutil.rmtree(python_dir)
    
    # Get platform information
    try:
        platform_info = get_platform_info()
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    print(f"Detected platform: {platform_info['system']} {platform_info['arch']}")
    print(f"Python version: {PYTHON_VERSION}")
    
    # Create temporary download directory
    temp_dir = webclient_dir / "temp_python_download"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Download the archive
        archive_path = temp_dir / platform_info['archive_name']
        download_file(platform_info['url'], archive_path)
        
        # Extract the archive
        extract_archive(archive_path, temp_dir, platform_info['extension'])
        
        # Find the extracted python directory (it's usually named 'python')
        extracted_dirs = [d for d in temp_dir.iterdir() if d.is_dir()]
        if not extracted_dirs:
            raise RuntimeError("No directory found after extraction")
        
        # Move the python directory to the final location
        extracted_python = extracted_dirs[0]
        print(f"Moving Python to {python_dir}...")
        shutil.move(str(extracted_python), str(python_dir))
        
        # Create a version info file
        version_info = {
            "python_version": PYTHON_VERSION,
            "platform": platform_info['system'],
            "architecture": platform_info['arch'],
            "download_url": platform_info['url']
        }
        
        version_file = python_dir / "standalone_version.json"
        with open(version_file, 'w') as f:
            json.dump(version_info, f, indent=2)
        
        print(f"✅ Python {PYTHON_VERSION} standalone successfully installed to {python_dir}")
        
        # Platform-specific instructions
        if platform_info['system'] == 'windows':
            python_exe = python_dir / "python.exe"
            print(f"\nPython executable: {python_exe}")
        else:
            python_exe = python_dir / "bin" / f"python{'.'.join(PYTHON_VERSION.split('.')[:2])}"
            print(f"\nPython executable: {python_exe}")
            
            # Make executable on Unix-like systems
            os.chmod(python_exe, 0o755)
        
        print("\nYou can now build the Electron application with:")
        print("  cd webclient")
        print("  npm install")
        print("  npm run build:electron")
        
    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            print(f"\nCleaning up temporary files...")
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()