"""Run with an isolated wheel interpreter; imports must work outside the checkout."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    env = dict(os.environ, HF_HUB_OFFLINE="1", LAYA_DEVICE="cpu", PYTHONUTF8="1")
    env.pop("PYTHONPATH", None)
    with tempfile.TemporaryDirectory(prefix="mcplaya-") as temp:
        cwd = Path(temp) / "Zoë Data"
        cwd.mkdir()
        for args in (["doctor"], ["config"], ["config", "--format", "vscode"],
                     ["config", "--format", "opencode"], ["config", "--format", "opencode-v1"]):
            proc = subprocess.run([sys.executable, "-m", "mcplaya", *args], cwd=cwd,
                                  env=env, capture_output=True, text=True, encoding="utf-8", timeout=60)
            if proc.returncode:
                raise RuntimeError(f"{args}: {proc.stdout}\n{proc.stderr}")
            json.loads(proc.stdout)
    print("Installed wheel: doctor and client configurations passed outside checkout")


if __name__ == "__main__":
    main()
