"""Create a deterministic Agensi archive, without binaries or hidden files."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]


def main():
    skill = ROOT / "skills/laya-decisions"
    entries = {"laya-decisions/" + p.relative_to(skill).as_posix(): p
               for p in skill.rglob("*") if p.is_file()}
    entries.update({"laya-decisions/" + name: ROOT / name for name in ("LICENSE", "NOTICE")})
    for name, path in entries.items():
        if path.is_symlink() or any(part.startswith(".") for part in Path(name).parts):
            raise ValueError("unsafe archive member")
        path.read_text(encoding="utf-8")
    output = ROOT / "dist/laya-decisions.zip"
    output.parent.mkdir(exist_ok=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for name, path in sorted(entries.items()):
            info = ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    print(output)


if __name__ == "__main__":
    main()
