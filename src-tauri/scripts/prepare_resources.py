#!/usr/bin/env python3
"""Prepare the Tauri bundle resources: standalone Python 3.12 with renardo and
its dependencies pre-installed (no pip at runtime) and the built web client.

Run before `tauri build`. Requires uv and npm."""

import shutil
import subprocess
import sys
from pathlib import Path

PYTHON_VERSION = "3.12"

HERE = Path(__file__).resolve().parent
TAURI_DIR = HERE.parent
ROOT = TAURI_DIR.parent
RESOURCES = TAURI_DIR / "resources"


def run(*cmd, **kw):
    print("+", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], check=True, shell=(sys.platform == "win32" and cmd[0] == "npm"), **kw)


def find_python(install_dir: Path) -> Path:
    for root in install_dir.glob("cpython-*"):
        exe = root / "python.exe" if sys.platform == "win32" else root / "bin" / "python3"
        if not root.is_symlink() and exe.exists():
            return root
    raise RuntimeError(f"no python found in {install_dir}")


def prune_tk(python_root: Path):
    """Drop Tk/IDLE: unused by the web server, and linuxdeploy cannot resolve libtk."""
    for pattern in ["lib/python3.*/lib-dynload/_tkinter*", "lib/python3.*/tkinter", "lib/python3.*/idlelib",
                    "lib/python3.*/turtledemo", "lib/python3.*/test", "lib/tcl*", "lib/tk*", "lib/libtcl*", "lib/libtk*",
                    "DLLs/_tkinter*", "DLLs/tcl*", "DLLs/tk*", "tcl", "Lib/tkinter", "Lib/idlelib", "Lib/test",
                    "lib/python3.*/site-packages/PIL/_imagingtk*", "Lib/site-packages/PIL/_imagingtk*"]:
        for path in python_root.glob(pattern):
            shutil.rmtree(path) if path.is_dir() else path.unlink()


def main():
    if RESOURCES.exists():
        shutil.rmtree(RESOURCES)
    RESOURCES.mkdir()

    run("npm", "run", "build", cwd=ROOT / "webclient")

    tmp = RESOURCES / "_uv_python"
    run("uv", "python", "install", PYTHON_VERSION, "--install-dir", tmp)
    python_root = find_python(tmp)
    shutil.move(str(python_root), str(RESOURCES / "python"))
    shutil.rmtree(tmp)

    exe = RESOURCES / "python" / ("python.exe" if sys.platform == "win32" else "bin/python3")
    purelib = subprocess.check_output(
        [str(exe), "-c", "import sysconfig;print(sysconfig.get_path('purelib'))"], text=True
    ).strip()
    # renardo and its dependencies, wheels matching this platform
    run("uv", "pip", "install", "--python", exe, "--target", purelib, ROOT)
    prune_tk(RESOURCES / "python")
    print("Resources ready in", RESOURCES)


if __name__ == "__main__":
    main()
