# SPDX-License-Identifier: GPL-3.0
from pathlib import Path

def _read_version():
    version_file = Path(__file__).parent.parent.parent.parent / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return "0.0.0"

__version__ = _read_version()
