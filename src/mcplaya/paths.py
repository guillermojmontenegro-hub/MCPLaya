"""Local user storage without assumptions about the host operating system."""
import os
import sys
from pathlib import Path


def database_path():
    override = os.environ.get("MCPLAYA_DB")
    if override:
        return Path(override).expanduser().resolve()
    home = Path.home()
    legacy = Path(os.environ.get("XDG_STATE_HOME") or home / ".local/state") / "mcplaya/sequences.sqlite3"
    if sys.platform == "win32":
        root = Path(os.environ.get("LOCALAPPDATA") or home / "AppData/Local")
    elif sys.platform == "darwin":
        root = home / "Library/Application Support"
    else:
        root = legacy.parent.parent
    native = root / "mcplaya/sequences.sqlite3"
    # Existing installations retain their history; do not move a live SQLite DB.
    if not native.exists() and legacy.is_file():
        return legacy
    return native
