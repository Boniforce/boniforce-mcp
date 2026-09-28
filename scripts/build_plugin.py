"""Build reproducible plugin and skills-only ZIPs without credentials/runtime files."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "boniforce-credit-check"


def build(*, target: str = "desktop", app_id: str | None = None,
          output_dir: Path | None = None) -> list[Path]:
    """Keep direct MCP declarations out of the ChatGPT web archive.

    An app ID is a registered connection, not a Plugin_ listing ID. This
    validates its shape only; account access must be tested in ChatGPT.
    """
    if target not in {"desktop", "chatgpt"}:
        raise ValueError("Target must be desktop or chatgpt")
    if target == "chatgpt" and (
        not app_id or not re.fullmatch(r"plugin_asdk_app_[A-Za-z0-9]+", app_id)
    ):
        raise ValueError(
            "ChatGPT requires a real registered MCP app ID (plugin_asdk_app_...). "
            "A Plugin_ listing URL is not an app connection. Register Boniforce "
            "in ChatGPT first; do not invent an ID."
        )
    if target == "desktop" and app_id is not None:
        raise ValueError("Use --target chatgpt with --app-id")
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
    contents = {p.relative_to(PLUGIN).as_posix(): p.read_bytes() for p in files}
    if target == "chatgpt":
        # The inline extension overrides the compatibility manifest. Wire both.
        manifest["extensions"]["com.openai"]["apps"] = "./.app.json"
        legacy["apps"] = "./.app.json"
        legacy.pop("mcpServers", None)
        for name in ("mcp.json", ".mcp.json"):
            contents.pop(name, None)
        contents["plugin.json"] = _json_bytes(manifest)
        contents[".codex-plugin/plugin.json"] = _json_bytes(legacy)
        contents[".app.json"] = _json_bytes({"apps": {"boniforce": {"id": app_id}}})
        contents["README.md"] = (
            "# Boniforce for ChatGPT\n\n"
            "This package uses the registered Boniforce app connection.\n"
            "Install it only where that app is available, complete its OAuth "
            "connection, then test list_reports in a new chat without creating "
            "a paid report.\n\n"
            "Uploading this ZIP does not publish the app or grant Free-plan "
            "access. Public distribution requires OpenAI review and publication. "
            "Account, region and app eligibility still apply. A Boniforce account "
            "is required; Boniforce credit charges are separate from the ChatGPT plan.\n"
        ).encode()
        # A direct MCP dependency can trigger a desktop connection prompt too.
        # ChatGPT receives the tools through .app.json, under its own namespace.
        for name in list(contents):
            if name.endswith("/agents/openai.yaml"):
                contents.pop(name)
        skill_path = "skills/boniforce-credit-check/SKILL.md"
        availability = (
            "1. Confirm that tools from the `boniforce` MCP server are available. "
            "If unavailable, tell the user to connect `https://mcp.boniforce.de/mcp` "
            "using OAuth and retry in a new conversation."
        )
        skill = contents[skill_path].decode()
        if availability not in skill:
            raise ValueError("Review the ChatGPT availability instructions after the skill changed")
        contents[skill_path] = skill.replace(availability, (
            "1. Discover tools from the connected Boniforce app; the host may namespace "
            "them differently. Confirm availability with the free `list_reports` call. "
            "If unavailable, ask the user to connect or reconnect the included Boniforce "
            "app in Settings → Plugins, select it, and retry in a new chat. "
            "Do not claim a server outage without a failed call, or send Free users "
            "through developer mode. An installed skill alone does not prove tool access."
        )).encode()
    releases = output_dir if output_dir is not None else ROOT / "releases"
    releases.mkdir(parents=True, exist_ok=True)
    outputs = []
    for kind in (("plugin", "skills") if target == "desktop" else ("chatgpt",)):
        archive_path = releases / f"boniforce-credit-check-{kind}-{version}.zip"
        with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as archive:
            for name, data in sorted(contents.items()):
                relative = Path(name)
                if kind == "skills":
                    if relative.parts[0] != "skills":
                        continue
                    relative = relative.relative_to("skills")
                info = ZipInfo(relative.as_posix(), date_time=(2026, 9, 28, 0, 0, 0))
                info.compress_type = ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, data)
        outputs.append(archive_path)
    suffix = "-chatgpt" if app_id is not None else ""
    checksum_path = releases / f"boniforce-credit-check{suffix}-{version}.sha256"
    checksum_path.write_text("".join(
        f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in outputs
    ))
    return [*outputs, checksum_path]


def _json_bytes(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=("desktop", "chatgpt"), default="desktop")
    parser.add_argument("--app-id", help="Registered Boniforce plugin_asdk_app_ ID, never a Plugin_ listing ID")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    try:
        outputs = build(target=args.target, app_id=args.app_id, output_dir=args.output_dir)
    except ValueError as exc:
        parser.error(str(exc))
    for output in outputs:
        print(output)
