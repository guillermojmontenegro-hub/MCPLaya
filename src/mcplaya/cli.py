"""Portable entry point; management commands never start the MCP transport."""
import argparse
import json
import os
import platform
import sqlite3
import sys
from importlib.metadata import version
from pathlib import Path

from .paths import database_path


def client_config(format):
    # Use this environment's interpreter, independent of PATH, cwd and shell.
    command = sys.executable
    args = ["-m", "mcplaya", "serve"]
    env = {"LAYA_DEVICE": os.environ.get("LAYA_DEVICE") or "cpu"}
    for key in ("MCPLAYA_DB", "LAYA_ACTION_MODEL", "HF_HOME", "HF_HUB_OFFLINE"):
        if os.environ.get(key):
            value = os.environ[key]
            if key != "HF_HUB_OFFLINE":
                value = str(database_path()) if key == "MCPLAYA_DB" else str(
                    Path(value).expanduser().resolve())
            env[key] = value
    if format == "opencode-v1":
        return {"mcp": {"mcplaya": {"type": "local", "command": [command, *args],
                                    "environment": env, "enabled": True}}}
    if format == "opencode":
        return {"mcp": {"servers": {"mcplaya": {"type": "local",
                "command": [command, *args], "environment": env}}}}
    entry = {"command": command, "args": args, "env": env}
    if format == "vscode":
        entry["type"] = "stdio"
        return {"servers": {"mcplaya": entry}}
    return {"mcpServers": {"mcplaya": entry}}


def doctor():
    """Check native inference imports, without loading or downloading models."""
    report = {"python": platform.python_version(), "executable": sys.executable,
              "system": platform.system(), "architecture": platform.machine(),
              "database": str(database_path()), "device": os.environ.get("LAYA_DEVICE") or "cpu",
              "packages": {}, "errors": []}
    try:
        for name in ("mcplaya", "laya", "mcp", "torch", "transformers", "numpy"):
            report["packages"][name] = version(name)
        import torch
        from laya import Agent, Router  # noqa: F401
        from transformers import AutoModel, AutoTokenizer  # noqa: F401
        # Exercise the Torch/NumPy ABI, a frequent failure on older machines.
        torch.zeros(1).numpy()
        torch.zeros(1, device=report["device"])
        with sqlite3.connect(":memory:") as db:
            db.execute("SELECT 1")
    except Exception as exc:
        report["errors"].append(f"{type(exc).__name__}: {exc}")
    report["ok"] = not report["errors"]
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description="Local Laya MCP server (stdio)")
    parser.add_argument("--version", action="version", version=version("mcplaya"))
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("serve", help="Run the stdio MCP server (default)")
    config = commands.add_parser("config", help="Print client configuration; does not edit any files")
    config.add_argument("--format", choices=("mcp", "vscode", "opencode", "opencode-v1"), default="mcp")
    commands.add_parser("doctor", help="Check installation without downloading models")
    args = parser.parse_args(argv)
    if args.command == "config":
        print(json.dumps(client_config(args.format), indent=2, ensure_ascii=True))
    elif args.command == "doctor":
        report = doctor()
        print(json.dumps(report, indent=2, ensure_ascii=True))
        if not report["ok"]:
            raise SystemExit(1)
    else:
        from .server import main as serve
        serve()
