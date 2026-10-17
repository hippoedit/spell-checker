# HippoEDIT Spell Checker

Canonical distribution repository for the HippoEDIT Spell Checker plugin.

Spell Checker is a normal HippoEDIT plugin that is bundled by default with the editor installer. It can be enabled/disabled independently and may be released independently while its editor compatibility contract permits.

## Current canonical release

The first canonical external release is `2.0.86`, bootstrapped from the exact SpellChecker binaries shipped in the accepted HippoEDIT 2.0.86 Unicode x86 and x64 installers.

The release ZIP is the binary distribution source of truth:

```text
spell-checker-2.0.86.zip
  package-info.xml
  x32u/SpellChecker.dll
  x64/SpellChecker.dll
```

The bootstrap verified the published installer SHA-256 values, the extracted DLL SHA-256 values, plugin GUID `CE3B04B4-AD3F-4827-A629-4C5149C4DAA4`, and PE file/product version `2.0.86` before creating the Release.

The old website `1.0.2.4` package is historical and is not the source for the current release: its DLLs differ from the binaries shipped with HippoEDIT 2.0.86, and its PDB archives correspond to those old DLLs.

## Release contract

Future releases are artifact-first rather than installer-derived. The editor build produces the x32 Unicode and x64 DLLs, and this repository's packager validates them and creates the canonical deterministic ZIP:

```bash
python3 tools/package_release.py \
  --x32u path/to/x32u/SpellChecker.dll \
  --x64 path/to/x64/SpellChecker.dll \
  --output-dir dist
```

The packager validates the stable plugin GUID, PE `FileVersion` and `ProductVersion` against `package-info.xml`, and the manifest's canonical x32u/x64 file contract. It prints the DLL and release ZIP SHA-256 values needed by downstream verification.

The installer must consume the DLLs from that canonical release artifact or byte-verify its bundled DLLs against it. The website plugin publisher pins the same Release tag/asset/digest. Neither consumer owns a separate SpellChecker binary copy.

See [`docs/release.md`](docs/release.md) for the release sequence and integration contract.
