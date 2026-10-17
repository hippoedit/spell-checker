import hashlib
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "package_release.py"
PACKAGE_INFO = ROOT / "package-info.xml"


def manifest_value(name: str) -> str:
    root = ET.parse(PACKAGE_INFO).getroot()
    for child in root:
        if child.tag.rsplit("}", 1)[-1] == name:
            return (child.text or "").strip()
    raise AssertionError(f"missing manifest value: {name}")


PLUGIN_ID = manifest_value("id")
VERSION = manifest_value("version")


def fake_dll(path: Path, plugin_id: str = PLUGIN_ID, version: str = VERSION) -> None:
    data = bytearray(b"MZ" + b"\0" * 62)
    data.extend(("{" + plugin_id + "}").encode("ascii"))
    for key in ("FileVersion", "ProductVersion"):
        while len(data) % 4:
            data.append(0)
        data.extend(key.encode("utf-16le") + b"\0\0")
        while len(data) % 4:
            data.append(0)
        data.extend(version.encode("utf-16le") + b"\0\0")
    path.write_bytes(bytes(data))


class PackageReleaseTest(unittest.TestCase):
    def run_tool(self, x32: Path, x64: Path, output: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(TOOL),
                "--manifest",
                str(PACKAGE_INFO),
                "--x32u",
                str(x32),
                "--x64",
                str(x64),
                "--output-dir",
                str(output),
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_builds_deterministic_canonical_zip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            x32 = root / "x32.dll"
            x64 = root / "x64.dll"
            output = root / "out"
            fake_dll(x32)
            fake_dll(x64)

            first = self.run_tool(x32, x64, output)
            self.assertEqual(0, first.returncode, first.stderr)

            archive = output / f"spell-checker-{VERSION}.zip"
            self.assertTrue(archive.is_file())
            first_digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            with zipfile.ZipFile(archive) as package:
                self.assertEqual(
                    [
                        "package-info.xml",
                        "x32u/SpellChecker.dll",
                        "x64/SpellChecker.dll",
                    ],
                    package.namelist(),
                )
                self.assertTrue(
                    all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in package.infolist())
                )

            second = self.run_tool(x32, x64, output)
            self.assertEqual(0, second.returncode, second.stderr)
            self.assertEqual(first_digest, hashlib.sha256(archive.read_bytes()).hexdigest())

    def test_rejects_wrong_plugin_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            x32 = root / "x32.dll"
            x64 = root / "x64.dll"
            fake_dll(x32, plugin_id="00000000-0000-0000-0000-000000000000")
            fake_dll(x64)

            result = self.run_tool(x32, x64, root / "out")

            self.assertNotEqual(0, result.returncode)
            self.assertIn("plugin id", result.stderr.lower())

    def test_rejects_wrong_binary_version(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            x32 = root / "x32.dll"
            x64 = root / "x64.dll"
            fake_dll(x32, version=VERSION + ".wrong")
            fake_dll(x64)

            result = self.run_tool(x32, x64, root / "out")

            self.assertNotEqual(0, result.returncode)
            self.assertIn("version", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
