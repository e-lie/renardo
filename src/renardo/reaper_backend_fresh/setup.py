"""
Installation de l'extension Rust REAPER fresh.

Vérifie la présence de REAPER, détecte l'OS/arch,
télécharge le bon binaire depuis les releases GitHub et l'installe dans UserPlugins.
"""

import os
import platform
import shutil
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

from renardo.logger import get_logger

logger = get_logger("reaper_fresh.setup")

GITHUB_REPO = "e-lie/renardo"
PLUGIN_INSTALL_NAME = "reaper_renardo_fresh"

# VERSION file est 4 niveaux au-dessus de ce fichier
_VERSION_FILE = Path(__file__).parent.parent.parent.parent / "VERSION"


def _get_version_tag() -> Optional[str]:
    """Lit le tag de version depuis le fichier VERSION à la racine du projet."""
    try:
        version = _VERSION_FILE.read_text().strip()
        return f"v{version}"
    except Exception as e:
        logger.warning(f"Could not read VERSION file ({_VERSION_FILE}): {e}")
        return None

# Chemins de config REAPER standard par OS
_REAPER_CONFIG_PATHS = {
    "linux": [
        Path.home() / ".config" / "REAPER",
    ],
    "darwin": [
        Path.home() / "Library" / "Application Support" / "REAPER",
    ],
    "windows": [
        Path(os.environ.get("APPDATA", "")) / "REAPER",
    ],
}


def find_reaper_resource_path() -> Optional[Path]:
    """
    Cherche le dossier de config REAPER (celui qui contient reaper.ini).
    Retourne le Path si trouvé, None sinon.
    """
    system = platform.system().lower()
    candidates = _REAPER_CONFIG_PATHS.get(system, [])

    for path in candidates:
        if path.is_dir() and any(
            (path / name).exists()
            for name in ("reaper.ini", "REAPER.INI", "Reaper.ini")
        ):
            logger.info(f"REAPER config found: {path}")
            return path

    logger.warning("REAPER config directory not found in standard locations.")
    return None


def get_user_plugins_dir(resource_path: Optional[Path] = None) -> Optional[Path]:
    """
    Retourne le dossier UserPlugins de REAPER.
    Utilise resource_path si fourni, sinon auto-détecte.
    """
    if resource_path is None:
        resource_path = find_reaper_resource_path()
    if resource_path is None:
        return None
    return resource_path / "UserPlugins"


def _get_artifact_name() -> Optional[str]:
    """
    Retourne le nom de l'artefact GitHub correspondant à l'OS et l'architecture courante.
    """
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Normalisation des noms d'architecture
    arch_map = {
        "x86_64": "x86_64",
        "amd64":  "x86_64",
        "aarch64": "aarch64",
        "arm64":   "arm64",   # macOS Apple Silicon
    }
    arch = arch_map.get(machine)

    if system == "linux":
        if arch == "x86_64":
            return "reaper_renardo_fresh_linux_x86_64.so"
        elif arch == "aarch64":
            return "reaper_renardo_fresh_linux_aarch64.so"

    elif system == "darwin":
        if arch == "x86_64":
            return "reaper_renardo_fresh_macos_x86_64.dylib"
        elif arch == "arm64":
            return "reaper_renardo_fresh_macos_arm64.dylib"

    elif system == "windows":
        if arch == "x86_64":
            return "reaper_renardo_fresh_windows_x86_64.dll"

    logger.error(f"Unsupported platform/arch: {system}/{machine}")
    return None


def _get_install_filename() -> Optional[str]:
    """Nom du fichier installé dans UserPlugins."""
    system = platform.system().lower()
    ext = {"linux": ".so", "darwin": ".dylib", "windows": ".dll"}.get(system)
    if ext is None:
        return None
    return PLUGIN_INSTALL_NAME + ext



def _download_file(url: str, dest: Path) -> bool:
    """Télécharge url vers dest avec une barre de progression simple."""
    try:
        logger.info(f"Downloading {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "renardo-setup"})
        with urllib.request.urlopen(req, timeout=60) as resp, open(dest, "wb") as f:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            block = 8192
            while True:
                chunk = resp.read(block)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded * 100 // total
                    print(f"\r  {pct}% ({downloaded}/{total} bytes)", end="", flush=True)
            print()
        return True
    except urllib.error.HTTPError as e:
        logger.error(f"HTTP {e.code} downloading {url}")
        return False
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return False


def install_reaper_extension(
    tag: Optional[str] = None,
    resource_path: Optional[Path] = None,
    force: bool = False,
) -> bool:
    """
    Télécharge et installe l'extension Rust dans UserPlugins de REAPER.

    Args:
        tag: Tag de release GitHub (ex: "v0.8.0"). Si None, utilise la dernière release.
        resource_path: Chemin du dossier de config REAPER. Si None, auto-détecté.
        force: Si True, réinstalle même si le fichier existe déjà.

    Returns:
        True si l'installation a réussi, False sinon.
    """
    # 1. Vérifier REAPER
    rpath = resource_path or find_reaper_resource_path()
    if rpath is None:
        logger.error(
            "REAPER config directory not found.\n"
            "Vérifiez que REAPER est installé et lancé au moins une fois.\n"
            "Chemins attendus :\n"
            "  Linux  : ~/.config/REAPER\n"
            "  macOS  : ~/Library/Application Support/REAPER\n"
            "  Windows: %APPDATA%\\REAPER"
        )
        return False

    # 2. Dossier UserPlugins
    plugins_dir = get_user_plugins_dir(rpath)
    plugins_dir.mkdir(parents=True, exist_ok=True)

    # 3. Nom du fichier cible
    install_filename = _get_install_filename()
    if install_filename is None:
        return False
    target_path = plugins_dir / install_filename

    if target_path.exists() and not force:
        logger.info(f"Extension already installed: {target_path}")
        logger.info("Use force=True to reinstall.")
        return True

    # 4. Résoudre le tag
    if tag is None:
        tag = _get_version_tag()
        if tag is None:
            logger.error("Could not determine version tag. Specify a tag manually.")
            return False
    logger.info(f"Using release: {tag}")

    # 5. Nom de l'artefact
    artifact_name = _get_artifact_name()
    if artifact_name is None:
        return False

    # 6. Téléchargement
    download_url = (
        f"https://github.com/{GITHUB_REPO}/releases/download/{tag}/{artifact_name}"
    )
    tmp_path = target_path.with_suffix(".tmp")
    try:
        if not _download_file(download_url, tmp_path):
            return False

        shutil.move(str(tmp_path), str(target_path))
        logger.info(f"Extension installed: {target_path}")
        logger.info("Restart REAPER to load the extension.")
        return True
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def check_extension_installed(resource_path: Optional[Path] = None) -> bool:
    """Vérifie si l'extension est déjà installée dans UserPlugins."""
    install_filename = _get_install_filename()
    if install_filename is None:
        return False
    plugins_dir = get_user_plugins_dir(resource_path)
    if plugins_dir is None:
        return False
    return (plugins_dir / install_filename).exists()


def setup_reaper_fresh(tag: Optional[str] = None, force: bool = False) -> bool:
    """
    Point d'entrée principal : vérifie REAPER et installe l'extension si nécessaire.

    Usage depuis le REPL Renardo :
        from renardo.reaper_backend_fresh.setup import setup_reaper_fresh
        setup_reaper_fresh()
    """
    logger.info("=== Renardo REAPER Fresh — Setup ===")

    rpath = find_reaper_resource_path()
    if rpath is None:
        logger.error("REAPER n'est pas détecté. Lancez REAPER au moins une fois.")
        return False

    logger.info(f"REAPER config: {rpath}")

    if check_extension_installed(rpath) and not force:
        logger.info("Extension already installed. Run with force=True to update.")
        return True

    return install_reaper_extension(tag=tag, resource_path=rpath, force=force)
