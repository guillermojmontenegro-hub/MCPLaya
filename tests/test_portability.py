import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from mcplaya import paths
from mcplaya.cli import client_config


@pytest.mark.parametrize("system,relative", [
    ("win32", "AppData/Local/mcplaya/sequences.sqlite3"),
    ("darwin", "Library/Application Support/mcplaya/sequences.sqlite3"),
    ("linux", ".local/state/mcplaya/sequences.sqlite3"),
])
def test_native_database_paths(monkeypatch, tmp_path, system, relative):
    for key in ("MCPLAYA_DB", "XDG_STATE_HOME", "LOCALAPPDATA"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(paths.sys, "platform", system)
    assert paths.database_path() == tmp_path / relative


@pytest.mark.parametrize("system,key", [("win32", "LOCALAPPDATA"), ("linux", "XDG_STATE_HOME")])
def test_os_directory_overrides(monkeypatch, tmp_path, system, key):
    monkeypatch.delenv("MCPLAYA_DB", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(paths.sys, "platform", system)
    monkeypatch.setenv(key, str(tmp_path / "Zoë Data"))
    assert paths.database_path() == tmp_path / "Zoë Data/mcplaya/sequences.sqlite3"


def test_explicit_database_and_legacy_history(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(paths.sys, "platform", "darwin")
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    monkeypatch.delenv("MCPLAYA_DB", raising=False)
    legacy = tmp_path / ".local/state/mcplaya/sequences.sqlite3"
    legacy.parent.mkdir(parents=True)
    legacy.touch()
    assert paths.database_path() == legacy
    native = tmp_path / "Library/Application Support/mcplaya/sequences.sqlite3"
    native.parent.mkdir(parents=True)
    native.touch()
    assert paths.database_path() == native
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("MCPLAYA_DB", "~/Zoë Data/custom.db")
    assert paths.database_path() == tmp_path / "Zoë Data/custom.db"


@pytest.mark.parametrize("format", ["mcp", "vscode", "opencode", "opencode-v1"])
def test_generated_config_launches_without_cwd_or_path(monkeypatch, tmp_path, format):
    # An executable path with spaces/backslashes must stay one JSON argument.
    for key in ("LAYA_DEVICE", "MCPLAYA_DB", "LAYA_ACTION_MODEL", "HF_HOME", "HF_HUB_OFFLINE"):
        monkeypatch.delenv(key, raising=False)
    config = client_config(format)
    if format == "opencode":
        entry = config["mcp"]["servers"]["mcplaya"]
    elif format == "opencode-v1":
        entry = config["mcp"]["mcplaya"]
    else:
        entry = config["servers" if format == "vscode" else "mcpServers"]["mcplaya"]
    command = entry["command"] if isinstance(entry["command"], list) else [entry["command"], *entry["args"]]
    assert command == [sys.executable, "-m", "mcplaya", "serve"]
    env = dict(os.environ, **entry.get("environment", entry.get("env", {})))
    assert env["LAYA_DEVICE"] == "cpu"
    # Help exits without starting stdio or importing model weights.
    result = subprocess.run([*command, "--help"], cwd=tmp_path, env=env,
                            capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert result.returncode == 0, result.stderr


def test_config_json_escapes_windows_paths(monkeypatch):
    executable = r"C:\Users\Zoë Smith\MCPLaya\Scripts\python.exe"
    monkeypatch.setattr(sys, "executable", executable)
    assert json.loads(json.dumps(client_config("mcp")))["mcpServers"]["mcplaya"]["command"] == executable


def test_config_preserves_explicit_settings(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MCPLAYA_DB", "history/local.db")
    monkeypatch.setenv("LAYA_ACTION_MODEL", "models/custom")
    monkeypatch.setenv("LAYA_DEVICE", "mps")
    env = client_config("mcp")["mcpServers"]["mcplaya"]["env"]
    assert env["MCPLAYA_DB"] == str(tmp_path / "history/local.db")
    assert env["LAYA_ACTION_MODEL"] == str(tmp_path / "models/custom")
    assert env["LAYA_DEVICE"] == "mps"
