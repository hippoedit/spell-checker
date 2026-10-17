#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

EXPECTED_PLUGIN_ID = "CE3B04B4-AD3F-4827-A629-4C5149C4DAA4"
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def child_text(root: ET.Element, local_name: str) -> str:
    for child in root:
        if child.tag.rsplit("}", 1)[-1] == local_name:
            return (child.text or "").strip()
    raise ValueError(f"manifest is missing <{local_name}>")


def manifest_contract(path: Path) -> tuple[str, str]:
    root = ET.parse(path).getroot()
    plugin_id = child_text(root, "id")
    version = child_text(root, "version")
    if plugin_id != EXPECTED_PLUGIN_ID:
        raise ValueError(f"unexpected plugin id in manifest: {plugin_id}")
    if not version:
        raise ValueError("manifest version is empty")

    required_files: set[str] = set()
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] == "require-file":
            name = (node.attrib.get("name") or "").strip()
            if name:
                required_files.add(name)
    expected = {"x32u/SpellChecker.dll", "x64/SpellChecker.dll"}
    if required_files != expected:
        raise ValueError(
            "manifest binary contract must require exactly "
            "x32u/SpellChecker.dll and x64/SpellChecker.dll"
        )
    return plugin_id, version


def pe_string_value(data: bytes, key: str) -> str:
    marker = key.encode("utf-16le") + b"\0\0"
    start = data.find(marker)
    if start < 0:
        raise ValueError(f"PE version resource is missing {key}")
    pos = start + len(marker)
    pos = (pos + 3) & ~3
    chars: list[bytes] = []
    while pos + 2 <= len(data):
        pair = data[pos:pos + 2]
        if pair == b"\0\0":
            break
        chars.append(pair)
        pos += 2
    if not chars:
        raise ValueError(f"PE version resource has empty {key}")
    return b"".join(chars).decode("utf-16le")


def validate_binary(path: Path, plugin_id: str, version: str) -> str:
    if not path.is_file():
        raise ValueError(f"missing DLL: {path}")
    data = path.read_bytes()
    if not data.startswith(b"MZ"):
        raise ValueError(f"not a PE DLL: {path}")
    guid = ("{" + plugin_id + "}").encode("ascii")
    if guid not in data:
        raise ValueError(f"plugin id {plugin_id} not found in {path}")
    for key in ("FileVersion", "ProductVersion"):
        actual = pe_string_value(data, key)
        if actual != version:
            raise ValueError(f"{key} {actual} in {path} does not match manifest version {version}")
    return hashlib.sha256(data).hexdigest()


def write_member(zf: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.create_system = 3
    info.compress_type = zipfile.ZIP_STORED
    info.external_attr = 0o100644 << 16
    zf.writestr(info, data)


def build(manifest: Path, x32u: Path, x64: Path, output_dir: Path) -> Path:
    plugin_id, version = manifest_contract(manifest)
    x32_sha = validate_binary(x32u, plugin_id, version)
    x64_sha = validate_binary(x64, plugin_id, version)
    output_dir.mkdir(parents=True, exist_ok=True)
    archive = output_dir / f"spell-checker-{version}.zip"
    tmp = archive.with_suffix(".zip.tmp")
    if tmp.exists():
        tmp.unlink()
    try:
        with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_STORED) as zf:
            write_member(zf, "package-info.xml", manifest.read_bytes())
            write_member(zf, "x32u/SpellChecker.dll", x32u.read_bytes())
            write_member(zf, "x64/SpellChecker.dll", x64.read_bytes())
        tmp.replace(archive)
    finally:
        if tmp.exists():
            tmp.unlink()
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    print(f"plugin_id={plugin_id}")
    print(f"version={version}")
    print(f"x32u_sha256={x32_sha}")
    print(f"x64_sha256={x64_sha}")
    print(f"asset={archive.name}")
    print(f"sha256={digest}")
    return archive


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the canonical HippoEDIT Spell Checker release ZIP.")
    parser.add_argument("--manifest", type=Path, default=Path("package-info.xml"))
    parser.add_argument("--x32u", type=Path, required=True)
    parser.add_argument("--x64", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        build(args.manifest, args.x32u, args.x64, args.output_dir)
    except (OSError, ET.ParseError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
