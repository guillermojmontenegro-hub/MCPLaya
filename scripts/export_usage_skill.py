"""Export one canonical usage skill into documented harness discovery layouts."""
import argparse
import json
import re
from datetime import date
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/mcplaya-decisions"
PROFILES = SKILL / "agents/profiles"


def load_profiles(directory=PROFILES):
    profiles = {}
    for path in sorted(Path(directory).glob("*.json")):
        profile = json.loads(path.read_text(encoding="utf-8"))
        if profile.get("format") != "mcplaya-skill-export-v1":
            raise ValueError(f"Unknown export profile format: {path.name}")
        identifier = profile.get("id", "")
        if identifier != path.stem or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", identifier):
            raise ValueError(f"Profile ID must match its filename: {path.name}")
        directory_name = profile["project_skill_directory"]
        destination = PurePosixPath(directory_name)
        if (destination.is_absolute() or len(destination.parts) != 2
                or destination.parts[1] != "skills" or not destination.parts[0].startswith(".")
                or any(part in (".", "..") for part in destination.parts)
                or "\\" in directory_name or ":" in directory_name):
            raise ValueError(f"Unsafe project skill directory: {directory_name}")
        if type(profile.get("include_openai_metadata")) is not bool:
            raise ValueError(f"Profile needs a metadata selection: {path.name}")
        if not profile.get("display_name") or not profile.get("documentation", "").startswith("https://"):
            raise ValueError(f"Profile needs its harness name and official documentation: {path.name}")
        date.fromisoformat(profile["verified_on"])
        profiles[identifier] = profile
    if not profiles:
        raise ValueError("No harness export profiles found")
    return profiles


def export_skill(profile, output_dir):
    destination = PurePosixPath(profile["project_skill_directory"]) / SKILL.name
    sources = [(PurePosixPath("SKILL.md"), SKILL / "SKILL.md")]
    for path in sorted((SKILL / "references").rglob("*")):
        if path.is_file() or path.is_symlink():
            sources.append((PurePosixPath(path.relative_to(SKILL).as_posix()), path))
    if profile["include_openai_metadata"]:
        sources.append((PurePosixPath("agents/openai.yaml"), SKILL / "agents/openai.yaml"))
    sources.extend((PurePosixPath(name), ROOT / name) for name in ("LICENSE", "NOTICE"))
    # Read every source before touching the output. Bundles contain regular text
    # files so extraction does not need symlinks or platform-specific privileges.
    contents = []
    for relative, path in sources:
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Skill source must be a regular file: {path}")
        data = path.read_bytes()
        data.decode("utf-8")
        contents.append(((destination / relative).as_posix(), data))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{SKILL.name}-{profile['id']}.zip"
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for name, data in sorted(contents):
            entry = ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            entry.compress_type = ZIP_DEFLATED
            archive.writestr(entry, data)
    return output


def main(argv=None):
    profiles = load_profiles()
    parser = argparse.ArgumentParser(description="Package MCPLaya's usage skill for local agent harnesses")
    parser.add_argument("--harness", choices=["all", *profiles], default="all")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--list", action="store_true", help="List harnesses and their native project directories")
    args = parser.parse_args(argv)
    if args.list:
        for identifier, profile in profiles.items():
            print(f"{identifier}: {profile['display_name']} -> {profile['project_skill_directory']}/{SKILL.name}")
        return
    selected = profiles.values() if args.harness == "all" else [profiles[args.harness]]
    for profile in selected:
        print(export_skill(profile, args.output_dir))


if __name__ == "__main__":
    main()
