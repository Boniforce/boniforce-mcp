"""Build reproducible plugin and skills-only ZIPs without credentials/runtime files."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "boniforce-credit-check"


def build() -> list[Path]:
    manifest = json.loads((PLUGIN / "plugin.json").read_text())
    legacy = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())
    for key in ("name", "version", "description"):
        if manifest[key] != legacy[key]:
            raise ValueError(f"Manifest mismatch: {key}")
    if manifest["extensions"]["com.openai"]["interface"] != legacy["interface"]:
        raise ValueError("Manifest presentation differs")
    version = manifest["version"]
    explicit = ["plugin.json", "mcp.json", ".codex-plugin/plugin.json", ".mcp.json", "LICENSE", "README.md"]
    files = [PLUGIN / name for name in explicit]
    for folder in ("skills", "assets"):
        files.extend(p for p in (PLUGIN / folder).rglob("*") if p.is_file()
                     and p.suffix in {".md", ".yaml", ".png"})
    if any(p.is_symlink() or not p.resolve().is_relative_to(PLUGIN.resolve()) for p in files):
        raise ValueError("Plugin files must remain inside the package")
    releases = ROOT / "releases"
    releases.mkdir(exist_ok=True)
    outputs = []
    for kind in ("plugin", "skills"):
        target = releases / f"boniforce-credit-check-{kind}-{version}.zip"
        with ZipFile(target, "w", compression=ZIP_DEFLATED) as archive:
            for path in sorted(files):
                relative = path.relative_to(PLUGIN)
                if kind == "skills":
                    if relative.parts[0] != "skills":
                        continue
                    relative = relative.relative_to("skills")
                info = ZipInfo(relative.as_posix(), date_time=(2026, 9, 28, 0, 0, 0))
                info.compress_type = ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes())
        outputs.append(target)
    checksum_path = releases / f"boniforce-credit-check-{version}.sha256"
    checksum_path.write_text("".join(
        f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in outputs
    ))
    return [*outputs, checksum_path]


if __name__ == "__main__":
    for output in build():
        print(output.relative_to(ROOT))
