import json
import os
import re
import subprocess
import sys
from pathlib import PurePosixPath
from zipfile import ZipFile

import pytest

from scripts import export_usage_skill as exporter


# Native discovery paths checked against each harness's official documentation.
LAYOUTS = {
    "codex": ".agents/skills",
    "claude-code": ".claude/skills",
    "cursor": ".cursor/skills",
    "copilot": ".github/skills",
    "opencode": ".opencode/skills",
    "gemini-cli": ".gemini/skills",
    "cline": ".cline/skills",
    "roo-code": ".roo/skills",
}


@pytest.mark.parametrize("identifier,directory", LAYOUTS.items())
def test_bundle_has_native_layout_and_complete_references(tmp_path, identifier, directory):
    profile = exporter.load_profiles()[identifier]
    assert profile["project_skill_directory"] == directory
    output = exporter.export_skill(profile, tmp_path / "Zoë Exports")
    base = PurePosixPath(directory) / "mcplaya-decisions"
    expected = {"SKILL.md", "LICENSE", "NOTICE"}
    expected.update(path.relative_to(exporter.SKILL).as_posix()
                    for path in (exporter.SKILL / "references").glob("*.md"))
    if identifier == "codex":
        expected.add("agents/openai.yaml")
    with ZipFile(output) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == {(base / name).as_posix() for name in expected}
        for name in expected:
            member = (base / name).as_posix()
            source = exporter.ROOT / name if name in ("LICENSE", "NOTICE") else exporter.SKILL / name
            assert archive.read(member) == source.read_bytes()
            assert archive.getinfo(member).external_attr >> 16 == 0o100644
            if name.endswith(".md"):
                for link in re.findall(r"\]\(([^)]+)\)", archive.read(member).decode("utf-8")):
                    if "://" not in link and not link.startswith("#"):
                        target = (PurePosixPath(member).parent / link.split("#")[0]).as_posix()
                        assert target in archive.namelist(), (member, link)


def test_export_is_reproducible(tmp_path):
    profile = exporter.load_profiles()["claude-code"]
    first = exporter.export_skill(profile, tmp_path / "first").read_bytes()
    second = exporter.export_skill(profile, tmp_path / "second").read_bytes()
    assert first == second


@pytest.mark.parametrize("directory", ["/tmp/skills", "../skills", ".claude/skills/../../outside", "C:/skills", ".claude\\skills"])
def test_profile_cannot_escape_project_layout(tmp_path, directory):
    profile = dict(exporter.load_profiles()["claude-code"], project_skill_directory=directory)
    (tmp_path / "claude-code.json").write_text(json.dumps(profile), encoding="utf-8")
    with pytest.raises(ValueError, match="Unsafe project skill directory"):
        exporter.load_profiles(tmp_path)


def test_export_cli_runs_outside_checkout_without_installing_anything(tmp_path):
    output = tmp_path / "Zoë Bundles"
    result = subprocess.run(
        [sys.executable, str(exporter.ROOT / "scripts/export_usage_skill.py"),
         "--harness", "all", "--output-dir", str(output)],
        cwd=tmp_path, env=dict(os.environ, PYTHONUTF8="1"),
        capture_output=True, text=True, encoding="utf-8", timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert {path.name for path in output.iterdir()} == {
        f"mcplaya-decisions-{identifier}.zip" for identifier in LAYOUTS
    }
    assert set(tmp_path.iterdir()) == {output}
